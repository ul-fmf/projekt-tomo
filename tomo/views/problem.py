# -*- coding: utf-8 -*-
import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt

from tomo.models import *
from tomo.utils import *


def student_contents(request, problem, user, authenticated):
    try:
        sub = Submission.objects.filter(user=user, problem=problem).latest('timestamp')
        preamble = sub.preamble
    except Submission.DoesNotExist:
        preamble = "\n{0}\n".format(problem.preamble)
    context = {
        'problem': problem,
        'parts': problem.parts.all(),
        'attempts': Attempt.objects.from_user(user).for_problem(problem).dict_by_part(),
        'preamble': preamble,
        'authenticated': authenticated
    }
    if authenticated:
        context['data'], context['signature'] = pack({
            'user': user.id,
            'problem': problem.id,
            'timestamp': str(problem.timestamp)
        })
    return render_to_string(problem.language.student_file,
                            context_instance=RequestContext(request, context))

def student_download(request, problem_id):
    problem = Problem.objects.get_for_user(problem_id, request.user)
    filename = "{0}.{1}".format(slugify(problem.title), problem.language.extension)
    contents = student_contents(request, problem, request.user,
                                 request.user.is_authenticated())
    return plain_text(filename, contents)

def api_student_contents(request):
    data = unpack(request.GET['data'], request.GET['signature'])
    user = get_object_or_404(User, id=data['user'])
    problem = Problem.objects.get_for_user(data['problem'], user)
    contents = student_contents(request, problem, user, True)
    return HttpResponse(contents)

@staff_member_required
def student_archive_download(request, problem_id, user_id):
    problem = Problem.objects.get_for_user(problem_id, request.user)
    user = get_object_or_404(User, id=user_id)
    username = user.get_full_name() or user.username
    filename = "{0}-{1}.{2}".format(slugify(problem.title), slugify(username), problem.language.extension)
    contents = student_contents(request, problem, user, False)
    return plain_text(filename, contents)

@staff_member_required
def move_up(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    order = problem.problem_set.get_problem_order()
    i = order.index(problem.id)
    if i - 1 >= 0:
        order[i - 1], order[i] = order[i], order[i - 1]
        problem.problem_set.set_problem_order(order)
    return redirect(problem)

@staff_member_required
def move_down(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    order = problem.problem_set.get_problem_order()
    i = order.index(problem.id)
    if i + 1 <= len(order) - 1:
        order[i + 1], order[i] = order[i], order[i + 1]
    problem.problem_set.set_problem_order(order)
    return redirect(problem)

@csrf_exempt
def student_upload(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    post = json.loads(request.raw_post_data)

    download = unpack(post['data'], post['signature'])
    user = get_object_or_404(User, id=download['user'])
    problem = Problem.objects.get_for_user(download['problem'], user)

    submission = Submission(user=user, problem=problem,
                            preamble=post['preamble'], source=post['source'])
    submission.save()

    attempts = dict((attempt['part'], attempt) for attempt in post['attempts'])
    old_attempts = Attempt.objects.from_user(user).for_problem(problem).dict_by_part()

    rejected = []

    for i, part in enumerate(problem.parts.all()):
        attempt = attempts.get(part.id, None)
        if attempt and attempt.get('solution').strip():
            solution = attempt['solution']
            errors = attempt.get('errors', [])
            attempt_challenge = attempt.get('challenge', [])
            part_challenge = json.loads(part.challenge)
            incorrect = ("testi" if errors else None)
            if not incorrect:
                if len(attempt_challenge) != len(part_challenge):
                    incorrect = "različno število izzivov"
                else:
                    for (j, ((k, x), (_, y))) in enumerate(zip(attempt_challenge, part_challenge)):
                        if x != y:
                            incorrect = "izziv #{0} ({1})".format(j + 1, k)
                            break
            correct = (incorrect is None)
            if incorrect:
                rejected.append((i + 1, incorrect))
            new = Attempt(part=part, submission=submission,
                          solution=solution, errors=json.dumps(errors),
                          correct=correct, active=True)
            old = old_attempts.get(part.id, None)
            if not old:
                new.save()
            elif old.correct != correct or old.solution != solution or old.errors != errors:
                old.active = False
                old.save()
                new.save()

    response = {
        'rejected' : rejected,
    }

    if download.get('timestamp', '') != str(problem.timestamp):
        data, sig = pack({
            'user': user.id,
            'problem': problem.id,
        })
        response['update'] = 'http://{0}:{1}{2}?{3}'.format(
            request.META['SERVER_NAME'],
            request.META['SERVER_PORT'],
            reverse('api_student_contents'),
            urlencode({'data': data, 'signature': sig})
        )

    return HttpResponse(json.dumps(response))

@staff_member_required
def create(request):
    verify(request.method == 'POST')
    problem_set = get_object_or_404(ProblemSet, id=request.POST['problem_set'])
    language = get_object_or_404(Language, id=request.POST['language'])
    problem = Problem(author=request.user, problem_set=problem_set,
                      language=language, title=request.POST['title'])
    problem.save()
    return redirect(problem)

def teacher_contents(request, problem, user):
    context = RequestContext(request, {
        'problem': problem,
        'parts': problem.parts.all(),
    })
    context['data'], context['signature'] = pack({
        'user': user.id,
        'problem': problem.id,
        'timestamp' : str(problem.timestamp),
    })
    return render_to_string(problem.language.teacher_file,
                            context_instance=RequestContext(request, context))

@staff_member_required
def teacher_download(request, problem_id=None):
    problem = Problem.objects.get_for_user(problem_id, request.user)
    filename = "{0}.{1}".format(slugify(problem.title), problem.language.extension)
    return plain_text(filename, teacher_contents(request, problem, request.user))

def api_teacher_contents(request):
    data = unpack(request.GET['data'], request.GET['signature'])
    user = get_object_or_404(User, id=data['user'])
    verify(user.is_staff)
    problem = Problem.objects.get_for_user(data['problem'], user)
    contents = teacher_contents(request, problem, user)
    return HttpResponse(contents)

@csrf_exempt
def teacher_upload(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    post = json.loads(request.raw_post_data)

    data = unpack(post['data'], post['signature'])
    user = get_object_or_404(User, id=data['user'])
    verify(user.is_staff)

    problem = get_object_or_404(Problem, id=data['problem'])

    old_parts = dict((part.id, part) for part in problem.parts.all())
    new_parts = []
    error = None
    messages = []

    if data.get('timestamp', '') != str(problem.timestamp):
        return(HttpResponse("NAPAKA: Uporabljate zastarelo verzijo datoteke. (Novo lahko pridobite na strežniku.)"))

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
                else:
                    old_parts.pop(new.id)
            new.description = part['description']
            new.solution = part['solution']
            new.validation = part['validation']
            new.challenge = new.challenge = json.dumps(part.get('challenge', []))
            if part_id == 0:
                messages.append("Nova podnaloga {0} je ustvarjena.".format(new.id))
            else:
                messages.append("Podnaloga {0} je shranjena.".format(new.id))
            new_parts.append(new)

    if not error:
        for p in old_parts:
            error = "Podnaloga {0} MANJKA. (Če jo želite zbrisati, uprabite spletni vmesnik.)".format(p)
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
        problem.save()
        for part in new_parts:
            part.save()
        problem.set_part_order([part.id for part in new_parts])

        data, sig = pack({
            'user': user.id,
            'problem': problem.id,
        })
        return HttpResponse(json.dumps({
                    'message': "\n".join(messages),
                    'update': 'http://{0}:{1}{2}?{3}'.format(
                        request.META['SERVER_NAME'],
                        request.META['SERVER_PORT'],
                        reverse('api_teacher_contents'),
                        urlencode({'data': data, 'signature': sig})
                    )
                }))
