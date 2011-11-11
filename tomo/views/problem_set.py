# -*- coding: utf-8 -*-
import hashlib, json, os

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response, redirect, render
from django.template import loader, Context, RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import csrf_exempt

from tomo.utils import *
from tomo.models import *

def download_contents(request, problem, user, authenticated):
    context = {
        'problem': problem,
        'parts': problem.parts.all(),
        'attempts': Attempt.objects.from_user(request.user).for_problem(problem).dict_by_part(),
        'authenticated': authenticated
    }
    if authenticated:
        context['data'], context['signature'] = pack({
            'user': user.id,
            'problem': problem.id
        })
    t = loader.get_template(problem.language.download_file)
    return t.render(RequestContext(request, context))

def view_problem_set(request, problem_set_id):
    problem_set = ProblemSet.objects.get_for_user(problem_set_id, request.user)
    parts_count = dict(Problem.objects.filter(problem_set=problem_set) \
                                      .annotate(Count('parts')) \
                                      .values_list('id', 'parts__count'))
    problems = problem_set.problems.all()
    attempts = Attempt.objects.for_problem_set(problem_set).from_user(request.user).dict_by_part()
    default_language = problems[0].language if problems.all() else None
    return render(request, "problem_set.html", {
        'problem_set': problem_set,
        'parts_count': parts_count,
        'problems': problems,
        'solved': problem_set.problems.success(request.user),
        'attempts': attempts,
        'languages': Language.objects,
        'default_language': default_language,
    })

@staff_member_required
def view_statistics(request, problem_set_id):
    problem_set = ProblemSet.objects.get_for_user(problem_set_id, request.user)
    attempts = {}
    for attempt in Attempt.objects.active().for_problem_set(problem_set).select_related('submission__user_id'):
        user_id = attempt.submission.user_id
        user_attempts = attempts.get(user_id, {})
        user_attempts[attempt.part_id] = attempt
        attempts[user_id] = user_attempts
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
        contents = download_contents(request, problem, request.user, request.user.is_authenticated()).encode('utf-8')
        files.append((filename, contents))
    return zip_archive(archivename, files)
