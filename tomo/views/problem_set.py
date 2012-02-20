# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string

from tomo.models import *
from tomo.utils import *
from tomo.views.problem import student_contents, teacher_contents

def view_problem_set(request, problem_set_id):
    problem_set = ProblemSet.objects.get_for_user(problem_set_id, request.user)
    problems = problem_set.problems.all()
    attempts = Attempt.objects.for_problem_set(problem_set).user_attempts(request.user)
    default_language = problems[0].language if problems else None
    print(cache._cache.keys())
    return render(request, "problem_set.html", {
        'courses': Course.user_courses(request.user),
        'problem_set': problem_set,
        'problems': problems,
        'all_courses': Course.objects.all(),
        'solved': ProblemSet.objects.success(request.user),
        'attempts': attempts,
        'languages': Language.objects,
        'default_language': default_language,
    })

@staff_member_required
def view_statistics(request, problem_set_id):
    problem_set = ProblemSet.objects.get_for_user(problem_set_id, request.user)
    attempts = dict((problem.id, {}) for problem in problem_set.problems.all())
    for attempt in Attempt.objects.active().for_problem_set(problem_set).select_related('submission__user', 'part__problem_id'):
        user = attempt.submission.user
        problem_id = attempt.part.problem_id
        user_attempts = attempts[problem_id].get(user, {})
        user_attempts[attempt.part_id] = attempt
        attempts[problem_id][user] = user_attempts
    return render(request, "statistics.html", {
        'courses': Course.user_courses(request.user),
        'problem_set': problem_set,
        'users': User.objects.filter(id__in=attempts.keys()).order_by('last_name'),
        'problems': problem_set.problems,
        'attempts': attempts
    })

def student_zip(request, problem_set_id):
    problem_set = ProblemSet.objects.get_for_user(problem_set_id, request.user)
    archivename = slugify(problem_set.title)
    files = []
    for i, problem in enumerate(problem_set.problems.all()):
        filename = "{0}/{1:02d}-{2}.{3}".format(archivename, i + 1, slugify(problem.title), problem.language.extension) # Select your files here.
        contents = student_contents(request, problem, request.user, request.user.is_authenticated()).encode('utf-8')
        files.append((filename, contents))
    return zip_archive(archivename, files)


def teacher_zip(request, problem_set_id):
    problem_set = ProblemSet.objects.get_for_user(problem_set_id, request.user)
    archivename = slugify(problem_set.title)
    files = []
    for problem in problem_set.problems.all():
        filename = "{0}/{1}.{2}".format(archivename, slugify(problem.title), problem.language.extension) # Select your files here.
        contents = teacher_contents(request, problem, request.user).encode('utf-8')
        files.append((filename, contents))
    return zip_archive(archivename, files)

@staff_member_required
def move(request, problem_set_id, k):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    k = int(k)
    order = problem_set.course.get_problemset_order()
    i = order.index(problem_set.id)
    if 0 <= i + k < len(order):
        order[i + k], order[i] = order[i], order[i + k]
        problem_set.course.set_problemset_order(order)
    return redirect(request.META.get('HTTP_REFERER', problem_set))

@staff_member_required
def toggle_solution_visibility(request, problem_set_id):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    if problem_set.solution_visibility == 'skrite':
        problem_set.solution_visibility = 'pogojno'
    elif problem_set.solution_visibility == 'pogojno':
        problem_set.solution_visibility = 'vidne'
    else:
        problem_set.solution_visibility = 'skrite'
    problem_set.save()
    return redirect(request.META.get('HTTP_REFERER', problem_set))

@staff_member_required
def toggle_visible(request, problem_set_id):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    problem_set.visible = not problem_set.visible
    problem_set.save()
    return redirect(request.META.get('HTTP_REFERER', problem_set))
