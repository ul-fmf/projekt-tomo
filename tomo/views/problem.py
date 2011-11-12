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
            'problem': problem.id,
            'timestamp' : str(problem.timestamp),
        })
    t = loader.get_template(problem.language.download_file)
    return t.render(RequestContext(request, context))


@csrf_exempt
def upload(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    post = json.loads(request.raw_post_data)

    download = unpack(post['data'], post['signature'])
    user = get_object_or_404(User, id=download['user'])
    problem = Problem.objects.get_for_user(download['problem'], user)

    submission = Submission(user=user, problem=problem,
                            source=post['source'])
    submission.save()

    attempts = dict((attempt['part'], attempt) for attempt in post['attempts'])
    old_attempts = Attempt.objects.from_user(user).for_problem(problem).dict_by_part()

    judgments = []

    for i, part in enumerate(problem.parts.all()):
        attempt = attempts.get(part.id, None)
        if attempt and attempt.get('solution'):
            solution = attempt['solution']
            errors = attempt.get('errors', [])
            attempt_challenge = attempt.get('challenge', [])
            part_challenge = json.loads(part.challenge)
            incorrect = ("testi" if errors else None)
            if not incorrect:
                if [k for (k,x) in attempt_challenge] != [m for (m,y) in part_challenge]:
                    incorrect = "različni izzivi"
                else:
                    for (j, ((k,x), (m,y))) in enumerate(zip(attempt_challenge, part_challenge)):
                        if x != y:
                            incorrect = "izziv #{0}, {1}".format(j,m)
                            break
            correct = (incorrect is None)
            judgments.append((i+1, incorrect))
            new = Attempt(part=part, submission=submission,
                          solution=solution, errors=json.dumps(errors),
                          correct=correct, active=True)
            old = old_attempts.get(part.id, None)
            if not old:
                new.save ()
            elif old.correct != correct or old.solution != solution or old.errors != errors:
                old.active = False
                old.save()
                new.save()

    response = { 'judgments' : judgments }
    if download.get('timestamp', '') != str(problem.timestamp):
        response['message'] = "NA VOLJO JE NOVA VERZIJA!"

    return HttpResponse(json.dumps(response))

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

    print(request.raw_post_data)
    post = json.loads(request.raw_post_data)

    data = unpack(post['data'], post['signature'])
    user = get_object_or_404(User, id=data['user'])
    problem = Problem.objects.get_for_user(data['problem'], user)
    old_parts = problem.parts.all()
    new_parts = []
    error = None
    messages = []

    if data.get('timestamp', '') != str(problem.timestamp):
        error = "NAPAKA: Uporabljate staro verzijo datoteke. (Novo lahko pridobite na strežniku.)"

    else:
        for part in post['parts']:
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
            new.challenge = new.challenge = json.dumps(part.get('challenge', []))
            new.save()
            if part_id == 0:
                messages.append("Nova podnaloga {0} je ustvarjena.".format(new.id))
            else:
                messages.append("Podnaloga {0} je shranjena.".format(new.id))
            new_parts.append(new.id)

    if not error:
        for p in old_parts:
            if p.id not in new_parts:
                error = "Podnaloga {0} MANJKA. (ÄŒe jo Å¾elite zbrisati, uprabite spletni vmesnik.)".format(p.id)
                break

    if error:
        messages.append(error)
        messages.append("\nNaloge NISO bile shranjene na strežnik.")
        return HttpResponse(json.dumps({
                    'message': "\n".join(messages)
                    }))
    else:
        problem.title = post['title']
        problem.description = post['description']
        problem.preamble = post['preamble']
        problem.set_part_order(new_parts)
        problem.save()

        data, signature = pack({
                'user': user.id,
                'problem': problem.id,
                'timestamp' : str(problem.timestamp),
                })
        context = RequestContext(request, {
                'problem': problem,
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
        'timestamp' : str(problem.timestamp),
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
    return plain_text(filename, contents)

