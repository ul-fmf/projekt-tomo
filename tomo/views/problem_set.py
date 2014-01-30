# -*- coding: utf-8 -*-
import datetime

from django.core.cache import cache
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string

from tomo.models import *
from tomo.utils import *
from tomo.views.problem import student_contents, teacher_contents

def view_problem_set(request, problem_set_id):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    verify(request.user.is_staff or problem_set.visible)
    problems = problem_set.problems.all()
    attempts = Attempt.objects.for_problem_set(problem_set).user_attempts(request.user)
    return render(request, "problem_set.html", {
        'courses': Course.user_courses(request.user),
        'problem_set': problem_set,
        'problems': problems,
        'all_courses': Course.objects.all(),
        'solved': ProblemSet.objects.success(request.user),
        'attempts': attempts,
        'languages': Language.objects
    })

@staff_member_required
def view_statistics(request, problem_set_id, limit):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    attempts = dict((problem.id, {}) for problem in problem_set.problems.all())
    user_ids = set()
    limit = int(limit)
    success = dict((part.id, {'correct': 0, 'incorrect': 0}) for problem in problem_set.problems.all() for part in problem.parts.all())
    active_attempts = Attempt.objects.active().for_problem_set(problem_set)
    if limit:
        cutoff = datetime.datetime.now() - datetime.timedelta(minutes=limit)
        active_attempts = active_attempts.filter(submission__timestamp__gt=cutoff)
    for attempt in active_attempts.select_related('submission__user', 'part__problem_id'):
        user_id = attempt.submission.user_id
        user_ids.add(user_id)
        problem_id = attempt.part.problem_id
        user_attempts = attempts[problem_id].get(user_id, {})
        user_attempts[attempt.part_id] = attempt
        success[attempt.part_id]['correct' if attempt.correct else 'incorrect'] += 1 
        attempts[problem_id][user_id] = user_attempts
    limits = [
        ("Zadnje pol ure", 30),
        ("Zadnji dve uri", 2 * 60),
        ("Zadnji dan", 24 * 60),
        ("Zadnji teden", 7 * 24 * 60),
        ("Vse", 0)
    ]
    return render(request, "statistics.html", {
        'courses': Course.user_courses(request.user),
        'problem_set': problem_set,
        'users': User.objects.filter(id__in=user_ids).order_by('last_name'),
        'problems': problem_set.problems,
        'attempts': attempts,
        'success': success,
        'limits': limits,
        'limit': limit
    })

@staff_member_required
def results_csv(request, problem_set_id):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    attempts = {}
    user_ids = set()
    active_attempts = Attempt.objects.active().for_problem_set(problem_set)
    for attempt in active_attempts.select_related('submission__user', 'part__problem_id'):
        user_id = attempt.submission.user_id
        user_ids.add(user_id)
        user_attempts = attempts.get(user_id, {})
        user_attempts[attempt.part_id] = attempt
        attempts[user_id] = user_attempts
    context = {
        'problem_set': problem_set,
        'users': User.objects.filter(id__in=user_ids).order_by('last_name'),
        'problems': problem_set.problems,
        'attempts': attempts
    }
    filename = "{0}.csv".format(slugify(problem_set.title))
    contents = render_to_string("results.csv",
                                context_instance=RequestContext(request, context))
    return plain_text(filename, contents, mimetype='text/csv')


def student_zip(request, problem_set_id):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    verify(request.user.is_staff or problem_set.visible)
    archivename = slugify(problem_set.title)
    files = []
    for i, problem in enumerate(problem_set.problems.all()):
        filename = "{0}/{1:02d}-{2}".format(archivename, i + 1, problem.filename())
        contents = student_contents(request, problem, request.user,
                                    request.user.is_authenticated()).encode('utf-8')
        files.append((filename, contents))
    return zip_archive(archivename, files)

@staff_member_required
def teacher_zip(request, problem_set_id):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    archivename = "{0}-edit".format(slugify(problem_set.title))
    files = []
    for problem in problem_set.problems.all():
        filename = "{0}/{1}".format(archivename, problem.filename()) # Select your files here.
        contents = teacher_contents(request, problem, request.user).encode('utf-8')
        files.append((filename, contents))
    return zip_archive(archivename, files)

@staff_member_required
def move(request, problem_set_id, shift):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    order = problem_set.course.get_problemset_order()
    old = order.index(problem_set.id)
    new = max(0, min(old + int(shift), len(order) - 1))
    order.insert(new, order.pop(old))
    problem_set.course.set_problemset_order(order)
    problem_set.course.save()
    return redirect(request.META.get('HTTP_REFERER', problem_set))

@staff_member_required
def toggle_solution_visibility(request, problem_set_id):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    next = {'skrite': 'pogojno', 'pogojno': 'vidne', 'vidne': 'skrite'}
    problem_set.solution_visibility = next[problem_set.solution_visibility]
    problem_set.save()
    return redirect(request.META.get('HTTP_REFERER', problem_set))

@staff_member_required
def toggle_visible(request, problem_set_id):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    problem_set.visible = not problem_set.visible
    problem_set.save()
    return redirect(request.META.get('HTTP_REFERER', problem_set))

@staff_member_required
def create(request):
    verify(request.method == 'POST')
    course = get_object_or_404(Course, id=request.POST['course'])
    problem_set = ProblemSet(course=course, title=request.POST['title'],
                             description=request.POST['description'],
                             visible=False, solution_visibility='pogojno')
    problem_set.save()
    return redirect(problem_set)
