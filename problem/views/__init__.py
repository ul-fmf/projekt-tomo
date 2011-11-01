# -*- coding: utf-8 -*-
import hashlib, json, os

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response, redirect, render
from django.template import loader, Context, RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import csrf_exempt

from tomo.problem.views.download import *
from tomo.problem.models import *

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

def get_problem_attempts(problem, user):
    if user.is_authenticated():
        attempts = Attempt.objects.filter(part__problem=problem,
                                          submission__user=user, active=True)
        return dict([
            (attempt.part_id, attempt) for attempt in attempts
        ])
    else:
        return {}

def download_contents(request, problem, user, authenticated):
    context = {
        'problem': problem,
        'parts': problem.parts.all(),
        'attempts': get_problem_attempts(problem, request.user),
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
    return plain_text(filename, contents)


@staff_member_required
def download_user(request, problem_id, user_id):
    problem = get_problem(problem_id, request.user)
    user = get_object_or_404(User, id=user_id)
    username = user.get_full_name() or user.username
    filename = "{0}-{1}.{2}".format(slugify(problem.title), slugify(username), problem.language.extension)
    contents = download_contents(request, problem, user, False)
    return plain_text(filename, contents)

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

    attempts = dict((attempt['part'], attempt) for attempt in json.loads(request.POST['attempts']))
    old_attempts = get_problem_attempts(problem, user)
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
    return plain_text(filename, contents)

@csrf_exempt
def update(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = unpack(request.POST['data'], request.POST['signature'])
    user = get_object_or_404(User, id=data['user'])
    problem = get_problem(data['problem'], user)
    old_parts = problem.parts.all()

    new_parts = []
    error = None
    messages = []
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
    default_language = problems.all()[0].language if problems.all() else None
    return render(request, "problem_set.html", {
        'problem_set': problem_set,
        'parts_count': parts_count,
        'problems': problems,
        'solved': solved,
        'attempts': attempts,
        'languages': Language.objects,
        'default_language': default_language,
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


def download_problem_set(request, problem_set_id):
    problem_set = get_problem_set(problem_set_id, request.user)
    archivename = slugify(problem_set.title)
    files = []
    for problem in problem_set.problems.all():
        filename = "{0}/{1}.{2}".format(archivename, slugify(problem.title), problem.language.extension) # Select your files here.
        contents = download_contents(request, problem, request.user, request.user.is_authenticated()).encode('utf-8')
        files.append((filename, contents))
    return zip_archive(archivename, files)
