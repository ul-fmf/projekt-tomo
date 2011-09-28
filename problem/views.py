# -*- coding: utf-8 -*-
import hashlib, json, random, time

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseNotAllowed, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import loader, Context, RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, AnonymousUser

from tomo.problem.models import Problem, Part, Submission, Attempt


def sign(text):
    sig = hashlib.md5(text + settings.SECRET_KEY).hexdigest()
    print(text)
    print(sig)
    return sig
def pack(data):
    text = json.dumps(data)
    return (text, sign(text))
def verify(test):
    if not test: raise PermissionDenied
def unpack(text, sig):
    verify(sign(text) == sig)
    return json.loads(text)

def get_problem(problem_id, user):
    problem = get_object_or_404(Problem, id=problem_id)
    if problem.revealed or user is problem.author:
        return problem
    else:
        raise Http404
def get_attempts(problem, user):
    if user.is_authenticated():
        attempts = Attempt.objects.filter(part__problem=problem,
                                      submission__user=user, active=True)
        return dict([
            (attempt.part_id, attempt) for attempt in attempts
        ])
    else:
        return {}

def render_to_file(name, template, context):
    if settings.DEBUG:
        response = HttpResponse(mimetype='text/html; charset=utf-8')
        response.write("<body><pre>")
        t = loader.get_template(template)
        response.write(t.render(context))
        response.write("</pre></body>")
    else:
        response = HttpResponse(mimetype='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(name)
        t = loader.get_template(template)
        response.write(t.render(context))
    return response

def download(request, problem_id):
    problem = get_problem(problem_id, request.user)
    solutions = {}
    for part_id, attempt in get_attempts(problem, request.user).items():
        solutions[part_id] = attempt.solution
    data, signature = pack({
        'user': request.user.id,
        'problem': problem.id,
    })
    context = RequestContext(request, {
        'problem': problem,
        'parts': problem.parts.all(),
        'solutions': solutions,
        'data': data,
        'signature': signature,
        'authenticated': request.user.is_authenticated()
    })
    filename = "{0}.py".format(slugify(problem.title))
    return render_to_file(filename, "python/download.py", context)

@staff_member_required
def download_user(request, problem_id, user_id):
    problem = get_problem(problem_id, request.user)
    user = get_object_or_404(User, id=user_id)
    username = user.get_full_name() or user.username
    solutions = {}
    for part_id, attempt in get_attempts(problem, request.user).items():
        solutions[part_id] = attempt.solution
    context = Context({
        'problem': problem,
        'parts': problem.parts.all(),
        'solutions': solutions,
        'authenticated': False
    })
    filename = "{0}-{1}.py".format(slugify(problem.title), slugify(username))
    return render_to_file(filename, "python/download.py", context)


@csrf_exempt
def upload(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    download = unpack(request.POST['data'], request.POST['signature'])
    user = get_object_or_404(User, id=download['user'])
    problem = get_problem(download['problem'], user)

    submission = Submission(user=user, problem=problem,
                            source=request.POST['source'])
    submission.save()
    attempts = json.loads(request.POST['attempts'])
    old_attempts = get_attempts(problem, user)
    incorrect = []

    for i, part in enumerate(problem.parts.all()):
        attempt = attempts[i]
        solution = attempt['solution']
        errors = json.dumps(attempt.get('errors', []))
        challenge = attempt.get('challenge', '')
        if solution:
            correct = challenge == part.challenge
            if not errors and not correct: incorrect.append(i + 1)
            old = old_attempts.get(part.id, None)
            new = Attempt(part=part, submission=submission,
                          solution=solution, errors=errors, correct=correct,
                          active=True)
            if old and (old.correct != correct or old.solution != solution):
                old.active = False
                old.save()
                new.save()
            elif not old:
                new.save()

    from django.db import connection
    for q in connection.queries:
        print (q['sql'][:100], q['duration'])
    return render_to_response("response.txt", Context({'incorrect': incorrect}))

@staff_member_required
def edit(request, problem_id=None):
    if problem_id:
        problem = get_problem(problem_id, request.user)
    else:
        problem = Problem(author=request.user)
        problem.save()
    data, signature = pack({
        'user': request.user.id,
        'problem': problem.id,
    })
    context = RequestContext(request, {
        'problem': problem,
        'parts': problem.parts.all(),
        'data': data,
        'signature': signature,
    })
    filename = "{0}.py".format(slugify(problem.title))
    return render_to_file(filename, "python/edit.py", context)

@csrf_exempt
def update(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    edit = unpack(request.POST['data'], request.POST['signature'])
    user = get_object_or_404(User, id=edit['user'])
    problem = get_problem(edit['problem'], user)
    parts = json.loads(request.POST['parts'])
    old_parts = problem.parts.all()
    new_parts = []

    problem.title = request.POST['title']
    problem.description = request.POST['description']
    problem.preamble = request.POST['preamble']

    for part in parts:
        try:
            new = Part.objects.get(id=part['part']) if part['part'] else Part(problem=problem)
        except Part.DoesNotExist:
            new = Part(problem=problem, id=part['part'])
        new.description = part['description']
        new.solution = part['solution']
        new.validation = part['validation']
        new.challenge = part.get('challenge', '')
        new.save()
        new_parts.append(new)
    for p in old_parts:
        if p not in new_parts:
            p.delete()
    problem.set_part_order([part.id for part in new_parts])
    problem.save()

    return HttpResponse('Vse naloge so shranjene.')
