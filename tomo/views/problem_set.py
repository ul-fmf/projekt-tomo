# -*- coding: utf-8 -*-
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string

from tomo.models import *
from tomo.utils import *
from tomo.views.problem import student_contents

def view_problem_set(request, problem_set_id):
    problem_set = ProblemSet.objects.get_for_user(problem_set_id, request.user)
    problems = problem_set.problems.all()
    attempts = Attempt.objects.for_problem_set(problem_set).from_user(request.user).dict_by_part()
    default_language = problems[0].language if problems else None
    return render(request, "problem_set.html", {
        'problem_set': problem_set,
        'problems': problems,
        'solved': problem_set.problems.success(request.user),
        'attempts': attempts,
        'languages': Language.objects,
        'default_language': default_language,
    })

@staff_member_required
def view_statistics(request, problem_set_id):
    problem_set = ProblemSet.objects.get_for_user(problem_set_id, request.user)
    attempts = dict((problem.id, {}) for problem in problem_set.problems.all())
    for attempt in Attempt.objects.active().for_problem_set(problem_set).select_related('submission__user_id', 'part__problem_id'):
        user_id = attempt.submission.user_id
        problem_id = attempt.part.problem_id
        user_attempts = attempts[problem_id].get(user_id, {})
        user_attempts[attempt.part_id] = attempt
        attempts[problem_id][user_id] = user_attempts
    return render(request, "statistics.html", {
        'problem_set': problem_set,
        'parts': [part.id for problem in problem_set.problems.all() for part in problem.parts.all()],
        'users': User.objects.filter(id__in=attempts.keys()).order_by('last_name'),
        'problems': problem_set.problems,
        'attempts': attempts
    })

def download_problem_set(request, problem_set_id):
    problem_set = ProblemSet.objects.get_for_user(problem_set_id, request.user)
    archivename = slugify(problem_set.title)
    files = []
    for problem in problem_set.problems.all():
        filename = "{0}/{1}.{2}".format(archivename, slugify(problem.title), problem.language.extension) # Select your files here.
        contents = student_contents(request, problem, request.user, request.user.is_authenticated()).encode('utf-8')
        files.append((filename, contents))
    return zip_archive(archivename, files)
