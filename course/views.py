from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import slugify

from tomo.course.models import Course, ProblemSet
from tomo.problem.models import Attempt
from tomo.problem.views import verify, download_zipfile

def get_problem_set(problem_set_id, user):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_id)
    verify(problem_set.visible or user.is_staff)
    return problem_set

def get_attempts(problem_set, user):
    if user.is_authenticated():
        attempts = Attempt.objects.filter(part__problem__problem_set=problem_set,
                                          submission__user=user, active=True)
        return dict([
            (attempt.part_id, attempt) for attempt in attempts
        ])
    else:
        return {}

def view_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    solved = dict((problem_set.id, problem_set.solved(request.user))
                  for problem_set in course.problem_sets.all())
    return render(request, "course.html", {
        'course': course,
        'solved': solved,
    })

def view_problem_set(request, problem_set_id):
    problem_set = get_problem_set(problem_set_id, request.user)
    solved = dict((problem.id, problem.solved(request.user))
                    for problem in problem_set.problems.all())
    attempts = get_attempts(problem_set, request.user)
    return render(request, "problem_set.html", {
        'problem_set': problem_set,
        'solved': solved,
        'attempts': attempts,
    })

def download_problem_set(request, problem_set_id):
    problem_set = get_problem_set(problem_set_id, request.user)
    return download_zipfile(request, problem_set.problems.all(), request.user, request.user.is_authenticated(), slugify(problem_set.title))
