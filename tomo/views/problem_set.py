# -*- coding: utf-8 -*-
import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from courses.models import Course, ProblemSet
from tomo.utils import verify, zip_archive
from tomo.models import Language, Attempt
from .problem import student_contents, teacher_contents

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
        'solved': ProblemSet.success(request.user),
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
def results_zip(request, problem_set_id):
    problemset = get_object_or_404(ProblemSet, id=problem_set_id)
    attempts = {}
    user_ids = set()
    active_attempts = Attempt.objects.active().for_problem_set(problemset)
    for attempt in active_attempts.select_related('submission__user_id'):
        user_id = attempt.submission.user_id
        user_ids.add(user_id)
        user_attempts = attempts.get(user_id, {})
        user_attempts[attempt.part_id] = attempt
        attempts[user_id] = user_attempts
    users = User.objects.filter(id__in=user_ids)
    archivename = "{0}-results".format(slugify(problemset.title))
    files = []
    for problem in problemset.problems.all():
        mass_template = problem.language.mass_file
        moss_template = problem.language.moss_file
        parts = problem.parts.all()
        for user in users.all():
            username = user.get_full_name() or user.username
            context = {
                'problem': problem,
                'parts': parts,
                'attempts': attempts[user.id],
                'user': user,
            }
            mass_filename = "{0}/{1}/{2}.{3}".format(archivename, slugify(problem.title), slugify(username), problem.language.extension)
            mass_contents = render_to_string(mass_template, context)
            files.append((mass_filename, mass_contents))
            moss_filename = "{0}/{1}-moss/{2}.{3}".format(archivename, slugify(problem.title), slugify(username), problem.language.extension)
            moss_contents = render_to_string(moss_template, context)
            files.append((moss_filename, moss_contents))
    context = {
        'problem_set': problemset,
        'users': User.objects.filter(id__in=user_ids).order_by('last_name'),
        'problems': [[part.id for part in problem.parts.all()] for problem in problemset.problems.all()],
        'attempts': attempts
    }
    filename = "{0}/{0}.csv".format(archivename)
    contents = render_to_string("results.csv",
                                context_instance=RequestContext(request, context))
    files.append((filename, contents))
    return zip_archive(archivename, files)


def student_zip(request, problem_set_id):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    verify(request.user.is_staff or problem_set.visible)
    archivename = slugify(problem_set.title)
    files = []
    for i, problem in enumerate(problem_set.problems.all()):
        filename = "{0}/{1:02d}-{2}".format(archivename, i + 1, problem.filename())
        contents = student_contents(request, problem, request.user,
                                    request.user.is_authenticated())
        files.append((filename, contents))
    return zip_archive(archivename, files)

@staff_member_required
def teacher_zip(request, problem_set_id):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    archivename = "{0}-edit".format(slugify(problem_set.title))
    files = []
    for problem in problem_set.problems.all():
        filename = "{0}/{1}".format(archivename, problem.filename()) # Select your files here.
        contents = teacher_contents(request, problem, request.user)
        files.append((filename, contents))
    return zip_archive(archivename, files)

@staff_member_required
def create(request):
    verify(request.method == 'POST')
    course = get_object_or_404(Course, id=request.POST['course'])
    problem_set = ProblemSet(course=course, title=request.POST['title'],
                             description=request.POST['description'],
                             visible=False, solution_visibility='pogojno')
    problem_set.save()
    return redirect(problem_set)
