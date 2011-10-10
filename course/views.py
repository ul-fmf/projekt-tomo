import collections, os, tempfile, zipfile

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.servers.basehttp import FileWrapper
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import slugify

from tomo.course.models import Course, ProblemSet
from tomo.problem.models import Attempt, Problem
from tomo.problem.views import verify, download_contents

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
    parts_count = dict(Problem.objects.filter(problem_set=problem_set) \
                                      .annotate(Count('parts')) \
                                      .values_list('id', 'parts__count'))
    solved = {}
    problems = problem_set.problems
    if request.user.is_authenticated():
        attempts = Attempt.objects.filter(submission__user=request.user,
                                          part__problem__problem_set=problem_set,
                                          active=True,
                                          correct=True) \
                                  .values('part__problem') \
                                  .annotate(correct=Count('part__problem'))
        for attempt in attempts:
            problem = attempt['part__problem']
            solved[problem] = solved.get(problem, 0) + int(attempt['correct'])
        for problem, correct in solved.items():
            solved[problem] = (100 * correct) / parts_count[problem]
    attempts = get_attempts(problem_set, request.user)
    return render(request, "problem_set.html", {
        'problem_set': problem_set,
        'parts_count': parts_count,
        'problems': problems,
        'solved': solved,
        'attempts': attempts,
    })

@staff_member_required
def view_statistics(request, problem_set_id):
    problem_set = get_problem_set(problem_set_id, request.user)
    parts = [part.id for problem in problem_set.problems.all() for part in problem.parts.all()]
    solved = {}
    problems = problem_set.problems
    if request.user.is_authenticated():
        attempts = Attempt.objects.filter(part__problem__problem_set=problem_set,
                                          active=True)
    attempts = {}
    for attempt in Attempt.objects \
                           .select_related('submission__user_id') \
                           .filter(part__problem__problem_set=problem_set,
                                   active=True):
        user_id = attempt.submission.user_id
        user_attempts = attempts.get(user_id, {})
        user_attempts[attempt.part_id] = attempt
        attempts[user_id] = user_attempts
    users = User.objects.filter(id__in=attempts.keys()).order_by('last_name')
    return render(request, "statistics.html", {
        'problem_set': problem_set,
        'parts': parts,
        'users': users,
        'problems': problems,
        'attempts': attempts
    })

def download_zipfile(files, archivename):
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    for filename, contents in files:
        archive.writestr(filename, contents)
    archive.close()
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename={0}.zip'.format(archivename)
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response


def download_problem_set(request, problem_set_id):
    problem_set = get_problem_set(problem_set_id, request.user)
    archivename = slugify(problem_set.title)
    files = []
    for problem in problem_set.problems.all():
        filename = "{0}/{1}.{2}".format(archivename, slugify(problem.title), problem.language.extension) # Select your files here.
        contents = download_contents(request, problem, request.user, request.user.is_authenticated()).encode('utf-8')
        files.append((filename, contents))
    return download_zipfile(files, archivename)
