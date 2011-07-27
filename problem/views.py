# -*- coding: utf-8 -*-
from hashlib import md5

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import loader, RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from tomo.problem.models import Problem, Submission, Solution, Part, Collection
from tomo.settings import SECRET_KEY


def sign(text):
    return md5(text + SECRET_KEY).hexdigest()

def verify(text, signature):
    return signature == sign(text)

def check_collection(collection, user):
    if collection.status == '10' and not user.is_staff:
        raise Http404

def collection_list(request):
    if request.user.is_staff:
        collections = Collection.objects.select_related().all()
    else:
        collections = Collection.objects.select_related().filter(status__gt=10)

    # solutions = {}
    # if request.user.is_authenticated():
    #     for sol in Solution.objects.filter(user=request.user).order_by('id'):
    #         solutions[sol.part] = sol

    return render_to_response("collections.html", RequestContext(request, {
        'collections': collections
    }))

def collection(request, object_id):
    collection = get_object_or_404(Collection.objects.select_related(), id=object_id)
    check_collection(collection, request.user)

    collection.modified_problems = collection.problems.all()
    for problem in collection.modified_problems:
        problem.modified_parts = problem.parts.all()
        for part in problem.modified_parts:
            part.user_solution = "neumna resitev"

    # if request.user.is_authenticated():
    #     # give the last solution for each part of the problem
    #     for sol in Solution.objects.filter(user=request.user, part__problem=problem).select_related('submission').order_by('id'):
    #         solutions[sol.part_id] = sol

    return render_to_response("collection.html", RequestContext(request, {
        'collection': collection
    }))

import datetime

# @staff_member_required
# def solutions(request, object_id):
#     problem = get_object_or_404(Problem, id=object_id)

#     solutions = {}
#     all_solutions = Solution.objects.filter(part__problem=problem).select_related('submission').order_by('-id')
#     for sol in all_solutions:
#         user_solutions = solutions.get(sol.user_id, {})
#         user_solutions[sol.part_id] = sol
#         solutions[sol.user_id] = user_solutions

#     return render_to_response("solutions.html", RequestContext(request, {
#         'problem': problem,
#         'solutions': solutions,
#         'parts': list(problem.parts.all())
#     }))


@staff_member_required
def solutions(request, object_id):
    from django.db.models import Max
    problem = get_object_or_404(Problem, id=object_id)

    parts = list(problem.parts.select_related('solutions').all())
    part0 = parts[0]

    part0sols = Solution.objects.filter(part__id=part0.id)
    users = part0sols.values('user').annotate(latest_submission=Max('submission__id')).values_list('latest_submission', flat=True)
    sols = Solution.objects.filter(submission__id__in=users).select_related('submission', 'user')
    subs = Submission.objects.filter(id__in=users).select_related('user')
    solutions = {}

    submissions = {}
    submissions = dict([(s.user, s) for s in subs])
    # all_solutions = Solution.objects.filter(part__problem=problem).select_related('submission').order_by('-id')
    for s in sols:
        user_solutions = solutions.get(s.user, {})
        user_solutions[s.part_id] = (s.correct, s.solution())
        solutions[s.user] = user_solutions

    # for sol in all_solutions:

    return render_to_response("solutions.html", RequestContext(request, {
        'problem': problem,
        'solutions': solutions,
        'submissions': submissions,
        'parts': list(problem.parts.all())
    }))


@login_required
def download_problem(request, object_id):
    problem = get_object_or_404(Problem, id=object_id)
    check_problem(problem, request.user)
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

@staff_member_required
def download_user_solutions(request, object_id, user_id):
    problem = get_object_or_404(Problem, id=object_id)
    user = get_object_or_404(User, id=user_id)
    slug = slugify(problem.name + "-" + user.get_full_name())
    solutions = {}
    for sol in Solution.objects.filter(user=user, part__problem=problem).order_by('id'):
        solutions[sol.part] = sol

    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}.py'.format(slug)
    t = loader.get_template('python/problem.py')
    c = RequestContext(request, {
        'problem': problem,
        'username': "",
        'signature': "",
        'solutions': solutions
    })
    response.write(t.render(c))
    return response

def download_anonymous_problem(request, object_id):
    problem = get_object_or_404(Problem, id=object_id)
    check_problem(problem, request.user)
    slug = slugify(problem.name)

    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}.py'.format(slug)
    t = loader.get_template('python/problem.py')
    c = RequestContext(request, {
        'problem': problem,
        'username': '',
        'signature': sign(str(problem.id)),
        'solutions': {}
    })
    response.write(t.render(c))
    return response


@staff_member_required
def edit_problem(request, object_id):
    problem = get_object_or_404(Problem, id=object_id)
    check_problem(problem, request.user)
    slug = slugify(problem.name)
    username = request.user.username

    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}.py'.format(slug)
    t = loader.get_template('python/edit.py')
    c = RequestContext(request, {
        'problem': problem,
        'username': username,
        'signature': sign(username + str(problem.id))
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

    response = HttpResponse(mimetype='text/plain')
    if username:
        user = get_object_or_404(User, username=username)
        check_problem(problem, user)
        submission = Submission(user=user, source=request.POST['source'],
                            download_ip=request.POST['download_ip'],
                            upload_ip=request.META['REMOTE_ADDR'])
        submission.save()
    
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
        response.write('Vse rešitve so shranjene.\n')
        if problem.status == '20':
            response.write('Rešujete izpit, zato bodo vse rešitve pregledane tudi ročno.')
    else:
        response.write('Naloge rešujete kot anonimni uporabnik!\n')
        response.write('Rešitve niso bile shranjene.')

    return response


@csrf_exempt
def upload_problem(request, object_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    problem = get_object_or_404(Problem, id=object_id)
    username = request.POST['username']
    signature = request.POST['signature']

    if not verify(username + str(problem.id), signature):
        return HttpResponseForbidden()

    response = HttpResponse(mimetype='text/plain')
    user = get_object_or_404(User, username=username)
    response.write('Naloge so shranjene.\n')
    ids = request.POST['problem_ids'].split(",")

    new_parts = []
    for id in map(int, ids):
        try:
            part = Part.objects.get(id=id) if id > 0 else Part(problem=problem)
        except Part.DoesNotExist:
            part = Part(problem=problem, id=id)
        part.description = request.POST['{0}_description'.format(id)]
        part.trial = request.POST['{0}_trial'.format(id)]
        part.solution = request.POST['{0}_solution'.format(id)]
        part.secret = request.POST['{0}_secret'.format(id)]
        part.save()
        new_parts.append(part)
    for p in problem.parts.all():
        if p not in new_parts:
            p.delete()
    problem.set_part_order([part.id for part in new_parts])
    problem.save()

    return response

