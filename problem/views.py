# -*- coding: utf-8 -*-
import hashlib, json

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response
from django.template import loader, Context, RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import csrf_exempt

from tomo.problem.models import Problem, Part, Submission, Attempt

def verify(cond):
    if not cond: raise PermissionDenied
def sign(text):
    return hashlib.md5(text + settings.SECRET_KEY).hexdigest()
def pack(data):
    text = json.dumps(data)
    return (text, sign(text))
def unpack(text, sig):
    verify(sign(text) == sig)
    return json.loads(text)

def get_problem(problem_id, user):
    problem = get_object_or_404(Problem, id=problem_id)
    verify(problem.problem_set.visible or user.is_staff)
    return problem

def get_attempts(problem, user):
    if user.is_authenticated():
        attempts = Attempt.objects.filter(part__problem=problem,
                                          submission__user=user, active=True)
        return dict([
            (attempt.part_id, attempt) for attempt in attempts
        ])
    else:
        return {}


def download_file(name, contents):
    response = HttpResponse(mimetype='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(name)
    response.write(contents)
    return response

def download_contents(request, problem, user, authenticated):
    context = {
        'problem': problem,
        'parts': problem.parts.all(),
        'attempts': get_attempts(problem, request.user),
        'authenticated': authenticated
    }
    if authenticated:
        context['data'], context['signature'] = pack({
            'user': user.id,
            'problem': problem.id
        })
    t = loader.get_template(problem.language.download_file)
    return t.render(RequestContext(request, context))

def download(request, problem_id):
    problem = get_problem(problem_id, request.user)
    filename = "{0}.{1}".format(slugify(problem.title), problem.language.extension)
    contents = download_contents(request, problem, request.user,
                                 request.user.is_authenticated())
    return download_file(filename, contents)


@staff_member_required
def download_user(request, problem_id, user_id):
    problem = get_problem(problem_id, request.user)
    user = get_object_or_404(User, id=user_id)
    username = user.get_full_name() or user.username
    filename = "{0}-{1}.{2}".format(slugify(problem.title), slugify(username), problem.language.extension)
    contents = download_contents(request, problem, user, False)
    return download_file(filename, contents)

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
    print(json.loads(request.POST['attempts']))
    attempts = dict((attempt['part'], attempt) for attempt in json.loads(request.POST['attempts']))
    old_attempts = get_attempts(problem, user)
    incorrect = []

    for i, part in enumerate(problem.parts.all()):
        attempt = attempts.get(part.id, None)
        if attempt:
            solution = attempt['solution']
            errors = attempt.get('errors', [])
            challenge = attempt.get('challenge', '')
            if solution:
                correct = challenge == part.challenge
                if not errors and not correct:
                    incorrect.append(i + 1)
                old = old_attempts.get(part.id, None)
                new = Attempt(part=part, submission=submission,
                              solution=solution, errors=json.dumps(errors),
                              correct=correct, active=True)
                if old and (old.correct != correct or old.solution != solution):
                    old.active = False
                    old.save()
                    new.save()
                elif not old:
                    new.save()

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
    filename = "{0}.{1}".format(slugify(problem.title), problem.language.extension)
    t = loader.get_template(problem.language.edit_file)
    contents = t.render(RequestContext(request, context))
    return download_file(filename, contents)

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
        if part['part']:
            try:
                new = Part.objects.get(id=part['part']) if part['part'] else Part(problem=problem)
            except Part.DoesNotExist:
                new = Part(problem=problem, id=part['part'])
        else:
            new = Part(problem=problem)
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
