# -*- coding: utf-8 -*-
import json
from copy import deepcopy
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from tomo.utils import verify, pack, unpack, plain_text
from problems.models import Language, Problem, Part
from submissions.models import Submission, Attempt
from courses.models import ProblemSet


def student_contents(request, problem, user, authenticated):
    context = {
        'problem': problem,
        'parts': problem.parts.all(),
        'attempts': Attempt.objects.for_problem(problem).user_attempts(user),
        'preamble': problem.preamble_for(user),
        'authenticated': authenticated,
        'user': user,
        'unsafe_port': settings.UNSAFE_PORT,
    }
    if authenticated:
        context['data'], context['signature'] = pack({
            'user': user.id,
            'problem': problem.id,
            'timestamp': str(problem.timestamp)
        })
    return render_to_string(problem.language.student_file,
                            context_instance=RequestContext(request, context))

def student_history_download(request, pk, user_id):
    problem = get_object_or_404(Problem, id=pk)
    verify(problem.problem_set.course.has_teacher(request.user))
    user = get_object_or_404(User, id=user_id)
    username = user.get_full_name() or user.username
    filename = "{0}-{1}-history.{2}".format(slugify(problem.title), slugify(username), problem.language.extension)
    submissions = []
    attempts = {}
    for submission in Submission.objects.filter(problem=problem, user=user):
        for attempt in submission.attempts.all():
            attempts[attempt.part_id] = attempt
        submissions.append({
                           'attempts': deepcopy(attempts),
                           'timestamp': submission.timestamp
                           })
    submissions.reverse()
    context = {
        'parts': problem.parts.all(),
        'submissions': submissions
    }
    return plain_text(filename, render_to_string(problem.language.student_file.replace("student", "history"),
                            context_instance=RequestContext(request, context)))

def student_download(request, pk):
    problem = get_object_or_404(Problem, id=pk)
    verify(problem.problem_set.course.has_teacher(request.user) or problem.problem_set.visible)
    contents = student_contents(request, problem, request.user,
                                 request.user.is_authenticated())
    return plain_text(problem.filename(), contents)

def api_student_contents(request):
    data = unpack(request.GET['data'], request.GET['signature'])
    user = get_object_or_404(User, id=data['user'])
    problem = get_object_or_404(Problem, id=data['problem'])
    verify(problem.problem_set.course.has_teacher(user) or problem.problem_set.visible)
    contents = student_contents(request, problem, user, True)
    return HttpResponse(contents)

def student_archive_download(request, pk, user_id):
    problem = get_object_or_404(Problem, id=pk)
    verify(problem.problem_set.course.has_teacher(request.user))
    user = get_object_or_404(User, id=user_id)
    username = user.get_full_name() or user.username
    filename = "{0}-{1}.{2}".format(slugify(problem.title), slugify(username), problem.language.extension)
    contents = student_contents(request, problem, user, False)
    return plain_text(filename, contents)

def move(request, pk, shift):
    problem = get_object_or_404(Problem, id=pk)
    verify(problem.problem_set.course.has_teacher(request.user))
    order = problem.problem_set.get_problem_order()
    old = order.index(problem.id)
    new = max(0, min(old + int(shift), len(order) - 1))
    order.insert(new, order.pop(old))
    problem.problem_set.set_problem_order(order)
    problem.problem_set.save()
    return redirect(request.META.get('HTTP_REFERER', problem))

def copy(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    problem = get_object_or_404(Problem, id=request.POST['problem_id'])
    problem_set = get_object_or_404(ProblemSet, id=request.POST['problem_set_id'])
    verify(problem_set.course.has_teacher(request.user))

    new_problem = deepcopy(problem)
    new_problem.id = None
    new_problem.problem_set = problem_set
    new_problem.save()

    for part in problem.parts.all():
        new_part = deepcopy(part)
        new_part.id = None
        new_part.problem = new_problem
        new_part.save()

    return redirect(new_problem)

@csrf_exempt
def student_upload(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    post = json.loads(request.body)

    download = unpack(post['data'], post['signature'])
    user = get_object_or_404(User, id=download['user'])
    problem = get_object_or_404(Problem, id=download['problem'])
    verify(problem.problem_set.course.has_teacher(user) or problem.problem_set.visible)

    submission = Submission(user=user, problem=problem, ip=request.META['REMOTE_ADDR'],
                            preamble=post['preamble'])
    submission.save()

    attempts = dict((attempt['part'], attempt) for attempt in post['attempts'])
    old_attempts = Attempt.objects.for_problem(problem).user_attempts(user)

    rejected = []
    update = download.get('timestamp', '') != str(problem.timestamp)

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
                    incorrect = 'Število izvedenih testov je {0} namesto {1}'.format(len(attempt_challenge), len(part_challenge))
                else:
                    for (j, ((hint, x), (_, y))) in enumerate(zip(attempt_challenge, part_challenge)):
                        if x != y:
                            incorrect = 'Namig: {0}'.format(hint) if hint else ''
                            break
            correct = (incorrect is None)
            if not correct:
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

    if update:
        data, sig = pack({
            'user': user.id,
            'problem': problem.id,
        })

        host = request.get_host().split(":")[0]
        response['update'] = 'http://{0}:{1}{2}?{3}'.format(
            host,
            settings.UNSAFE_PORT,
            reverse('api_student_contents'),
            urlencode({'data': data, 'signature': sig})
        )

    return HttpResponse(json.dumps(response))

def create(request):
    verify(request.method == 'POST')
    problem_set = get_object_or_404(ProblemSet, id=request.POST['problem_set'])
    verify(problem_set.course.has_teacher(request.user))
    language = get_object_or_404(Language, id=request.POST['language'])
    problem = Problem(author=request.user, problem_set=problem_set,
                      language=language, title=request.POST['title'])
    problem.save()
    return redirect(problem)

def teacher_contents(request, problem, user):
    context = RequestContext(request, {
        'problem': problem,
        'parts': problem.parts.all(),
        'user': user,
        'unsafe_port': settings.UNSAFE_PORT,
    })
    context['data'], context['signature'] = pack({
        'user': user.id,
        'problem': problem.id,
        'timestamp' : str(problem.timestamp),
    })
    return render_to_string(problem.language.teacher_file,
                            context_instance=RequestContext(request, context))

def dump_contents(request, problem):
    context = RequestContext(request, {
        'problem': problem,
        'parts': problem.parts.all(),
    })
    return render_to_string(problem.language.dump_file, context)

def teacher_download(request, pk=None):
    problem = get_object_or_404(Problem, id=pk)
    verify(problem.problem_set.course.has_teacher(request.user))
    return plain_text(problem.filename(), teacher_contents(request, problem, request.user))

class PartDelete(DeleteView):
    model = Part
    def get_success_url(self):
        return self.object.problem.get_absolute_url()

    def get_object(self, *args, **kwargs):
        obj = super(PartDelete, self).get_object(*args, **kwargs)
        verify(obj.problem.problem_set.course.has_teacher(self.request.user))
        return obj

    def get_context_data(self, **kwargs):
        context = super(PartDelete, self).get_context_data(**kwargs)
        attempts = self.object.attempts.filter(active=True).select_related('submission__timestamp', 'submission__user').order_by('submission__timestamp')
        context['attempts'] = attempts
        return context

class ProblemDelete(DeleteView):
    model = Problem
    def get_success_url(self):
        return self.object.problem_set.get_absolute_url()

    def get_object(self, *args, **kwargs):
        obj = super(ProblemDelete, self).get_object(*args, **kwargs)
        verify(obj.problem_set.course.has_teacher(self.request.user))
        return obj

    def get_context_data(self, **kwargs):
        context = super(ProblemDelete, self).get_context_data(**kwargs)
        attempts = {}
        submissions = {}
        user_ids = set()
        active_attempts = Attempt.objects.active().for_problem(self.object)
        for attempt in active_attempts.select_related('submission__user'):
            user_id = attempt.submission.user_id
            user_ids.add(user_id)
            user_attempts = attempts.get(user_id, {})
            user_attempts[attempt.part_id] = attempt
            attempts[user_id] = user_attempts
            submissions[user_id] = attempt.submission
        parts = self.object.parts.all()
        sorted_attempts = []
        for user in User.objects.filter(id__in=user_ids).order_by('last_name'):
            sorted_attempts.append((user, submissions[user.id], [attempts[user.id].get(part.id) for part in parts]))
        context['attempts'] = sorted_attempts
        return context


class ProblemCreate(CreateView):
    model = Problem
    fields = ['title', 'language', 'description']

    def get_context_data(self, **kwargs):
        context = super(ProblemCreate, self).get_context_data(**kwargs)
        problem_set = get_object_or_404(ProblemSet, id=self.kwargs['problem_set_id'])
        context['problem_set'] = problem_set
        return context

    def form_valid(self, form):
        problem_set = get_object_or_404(ProblemSet, id=self.kwargs['problem_set_id'])
        form.instance.author = self.request.user
        form.instance.problem_set = problem_set
        verify(problem_set.course.has_teacher(self.request.user))
        return super(ProblemCreate, self).form_valid(form)


class ProblemUpdate(UpdateView):
    model = Problem
    fields = ['title', 'language', 'description']

    def get_object(self, *args, **kwargs):
        obj = super(ProblemUpdate, self).get_object(*args, **kwargs)
        verify(obj.problem_set.course.has_teacher(self.request.user))
        return obj

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(ProblemUpdate, self).form_valid(form)


def api_teacher_contents(request):
    data = unpack(request.GET['data'], request.GET['signature'])
    user = get_object_or_404(User, id=data['user'])
    problem = get_object_or_404(Problem, id=data['problem'])
    verify(problem.problem_set.course.has_teacher(user))
    contents = teacher_contents(request, problem, user)
    return HttpResponse(contents)

@csrf_exempt
def teacher_upload(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    post = json.loads(request.body)

    data = unpack(post['data'], post['signature'])
    user = get_object_or_404(User, id=data['user'])

    problem = get_object_or_404(Problem, id=data['problem'])
    verify(problem.problem_set.course.has_teacher(user))

    old_parts = dict((part.id, part) for part in problem.parts.all())
    new_parts = []
    error = None
    messages = []
    update_data, sig = pack({
        'user': user.id,
        'problem': problem.id,
    })
    host = request.get_host().split(":")[0]
    update_url = 'http://{0}:{1}{2}?{3}'.format(
        host,
        settings.UNSAFE_PORT,
        reverse('api_teacher_contents'),
        urlencode({'data': update_data, 'signature': sig})
    )

    if data.get('timestamp', '') != str(problem.timestamp):
        return HttpResponse(json.dumps({
            'message': "NAPAKA: Uporabljate zastarelo verzijo datoteke.",
            'update': update_url
        }))

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
        for part in new_parts:
            part.save()
        problem.set_part_order([part.id for part in new_parts])
        problem.save()

        return HttpResponse(json.dumps({
                    'message': "\n".join(messages),
                    'update': update_url
                }))
