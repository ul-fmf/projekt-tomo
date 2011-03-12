# -*- coding: utf-8 -*-
from hashlib import md5

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import loader, RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from tomo.problem.models import Problem, Submission, Solution
from tomo.settings import SECRET_KEY


def sign(text):
    return md5(text + SECRET_KEY).hexdigest()

def verify(text, signature):
    return signature == sign(text)

def problem_list(request):
    problems = Problem.objects.all()

    solutions = {}
    if request.user.is_authenticated():
        for sol in Solution.objects.filter(user=request.user).order_by('id'):
            solutions[sol.part] = sol

    return render_to_response("problems.html", RequestContext(request, {
        'problem_list': problems
    }))

def problem(request, object_id):
    problem = get_object_or_404(Problem, id=object_id)

    solutions = {}
    if request.user.is_authenticated():
        for sol in Solution.objects.filter(user=request.user, part__problem=problem).order_by('id'):
            solutions[sol.part] = sol

    return render_to_response("problem.html", RequestContext(request, {
        'problem': problem,
        'solutions': solutions
    }))


@login_required
def download_problem(request, object_id):
    problem = get_object_or_404(Problem, id=object_id)
    slug = slugify(problem.name)
    username = request.user.username

    solutions = {}
    if request.user.is_authenticated():
        for sol in Solution.objects.filter(user=request.user, part__problem=problem).order_by('id'):
            solutions[sol.part] = sol

    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}.py'.format(slug)
    t = loader.get_template('python/problem.py')
    c = RequestContext(request, {
        'problem': problem,
        'username': username,
        'signature': sign(username + str(problem.id)),
        'solutions': solutions
    })
    response.write(t.render(c))
    return response


@csrf_exempt
def upload_solution(request, object_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    problem = get_object_or_404(Problem, id=object_id)
    username = request.POST['username']
    signature = request.POST['signature']

    if not verify(username + str(problem.id), signature):
        return HttpResponseForbidden()

    user = get_object_or_404(User, username=username)
    submission = Submission(user=user, source=request.POST['source'],
                        download_ip=request.POST['download_ip'],
                        upload_ip=request.META['REMOTE_ADDR'])
    submission.save()
    
    response = HttpResponse(mimetype='text/plain')
    response.write('Vse rešitve so shranjene.\n')
    for part in problem.parts.all():
        label = request.POST.get('{0}_label'.format(part.id))
        if label:
            start = request.POST['{0}_start'.format(part.id)]
            end = request.POST['{0}_end'.format(part.id)]
            secret = request.POST.get('{0}_secret'.format(part.id))
            correct = secret == part.secret
            if secret and not correct:
                response.write('Rešitev naloge {0}) je zavrnjena.'.format(label))
                response.write('Obvestite asistenta.\n')
            s = Solution(user=user, part=part, submission=submission,
                         start=start, end=end, correct=correct, label=label)
            s.save()

    return response

