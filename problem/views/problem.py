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

from tomo.problem.utils import *
from tomo.problem.models import *


def problem_file(request, problem_id, student_id=None):
    problem = get_object_or_404(Problem, id=problem_id)
    verify(problem.visible(request.user))
    if student_id:
        verify(request.user.is_staff)
        student = get_object_or_404(User, id=student_id)
        name = "{0}-{1}.{2}".format(slugify(problem.title),
                                    slugify(user.get_full_name()),
                                    problem.language.extension)
        contents = problem_file(problem, student, live_file=False)
    else:
        student = request.user
        name = "{0}.{1}".format(slugify(problem.title),
                                problem.language.extension)
        contents = problem_file(problem, student)
    return plain_text(name, contents)
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


@csrf_exempt
def upload(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    download = unpack(request.POST['data'], request.POST['signature'])
    user = get_object_or_404(User, id=download['user'])
    problem = Problem.objects.get_for_user(download['problem'], user)

    submission = Submission(user=user, problem=problem,
                            source=request.POST['source'])
    submission.save()

    attempts = dict((attempt['part'], attempt) for attempt in json.loads(request.POST['attempts']))
    old_attempts = Attempt.objects.from_user(request.user).for_problem(problem).dict_by_part()
    incorrect = {}
    challenges = []

    for i, part in enumerate(problem.parts.all()):
        attempt = attempts.get(part.id, None)
        if attempt:
            solution = attempt['solution']
            errors = attempt.get('errors', [])
            challenge = attempt.get('challenge', '')
            if solution:
                correct = challenge == part.challenge
                if not errors and not correct:
                    incorrect[i + 1] = (challenge, part.challenge)
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
def create(request):
    verify(request.method == 'POST')
    problem_set = get_object_or_404(ProblemSet, id=request.POST['problem_set'])
    language = get_object_or_404(Language, id=request.POST['language'])
    problem = Problem(
        author=request.user,
        problem_set=problem_set,
        language=language,
        title=request.POST['title']
    )
    problem.save()
    return redirect(problem)

@csrf_exempt
def update(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = unpack(request.POST['data'], request.POST['signature'])
    user = get_object_or_404(User, id=data['user'])
    problem = Problem.objects.get_for_user(data['problem'], user)
    old_parts = problem.parts.all()

    new_parts = []
    error = None
    messages = []

    print ("HA HAHA {0} AND {1}".format(request.POST['timestamp'], str(problem.timestamp)))
    if 'timestamp' not in request.POST or request.POST['timestamp'] != str(problem.timestamp):
        error = "NAPAKA: Uporabljate staro verzijo datoteke. (Novo lahko pridobite na strežniku.)"

    else:
        for part in json.loads(request.POST['parts']):
            part_id = int(part['part'])
            if part_id == 0:
                new = Part(problem=problem)
            else:
                try:
                    new = Part.objects.get(id=part['part'])
                    if new.id in new_parts:
                        error = "NAPAKA: podnaloga {0} se ponavlja.".format(new.id)
                        break
                    elif new.problem != problem:
                        error = "NAPAKA: podnaloga {0} ima neveljaven id.".format(new.id)
                        break
                except Part.DoesNotExist:
                    error = "NAPAKA: podnaloga {0} ima neveljaven id.".format(new.id)
                    break
            new.description = part['description']
            new.solution = part['solution']
            new.validation = part['validation']
            new.challenge = part.get('challenge', '')
            new.save()
            if part_id == 0:
                messages.append("Nova podnaloga {0} je ustvarjena.".format(new.id))
            else:
                messages.append("Podnaloga {0} je shranjena.".format(new.id))
            new_parts.append(new.id)

    if error:
        messages.append(error)
        messages.append("\nNaloge NISO bile shranjene na strežnik.")
        return HttpResponse(json.dumps({
                    'message': "\n".join(messages)
                    }))
    else:
        for p in old_parts:
            if p.id not in new_parts:
                Part.objects.filter(id=p.id).delete()
                messages.append("Podnaloga {0} je IZBRISANA.".format(p.id))
        problem.title = request.POST['title']
        problem.description = request.POST['description']
        problem.preamble = request.POST['preamble']
        problem.set_part_order(new_parts)
        problem.save()

        data, signature = pack({
                'user': user.id,
                'problem': problem.id,
                })
        context = RequestContext(request, {
                'problem': problem,
                'timestamp' : str(problem.timestamp),
                'parts': problem.parts.all(),
                'data': data,
                'signature': signature,
                })
        t = loader.get_template(problem.language.edit_file)
        contents = t.render(RequestContext(request, context))

        return HttpResponse(json.dumps({
                    'message': "\n".join(messages),
                    'contents': contents
                    }))

def download(request, problem_id):
    problem = Problem.objects.get_for_user(problem_id, request.user)
    filename = "{0}.{1}".format(slugify(problem.title), problem.language.extension)
    contents = download_contents(request, problem, request.user,
                                 request.user.is_authenticated())
    return plain_text(filename, contents)


@staff_member_required
def download_user(request, problem_id, user_id):
    return problem_file(request, problem_id, user_id)
    problem = Problem.objects.get_for_user(problem_id, request.user)
    user = get_object_or_404(User, id=user_id)
    username = user.get_full_name() or user.username
    filename = "{0}-{1}.{2}".format(slugify(problem.title), slugify(username), problem.language.extension)
    contents = download_contents(request, problem, user, False)
    return plain_text(filename, contents)

@staff_member_required
def edit(request, problem_id=None):
    if problem_id:
        problem = Problem.objects.get_for_user(problem_id, request.user)
    else:
        problem = Problem(author=request.user)
        problem.save()
    data, signature = pack({
        'user': request.user.id,
        'problem': problem.id,
    })
    context = RequestContext(request, {
        'problem': problem,
        'timestamp' : str(problem.timestamp),
        'parts': problem.parts.all(),
        'data': data,
        'signature': signature,
    })
    filename = "{0}.{1}".format(slugify(problem.title), problem.language.extension)
    t = loader.get_template(problem.language.edit_file)
    contents = t.render(RequestContext(request, context))
    return plain_text(filename, contents)

