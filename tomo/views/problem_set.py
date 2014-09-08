# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from courses.models import Course, ProblemSet
from tomo.utils import verify, zip_archive
from problems.models import Language
from submissions.models import Attempt
from .problem import student_contents, teacher_contents

def view_problem_set(request, pk):
    problem_set = get_object_or_404(ProblemSet, id=pk)
    user_is_teacher = problem_set.course.has_teacher(request.user)
    verify(user_is_teacher or problem_set.visible)
    problems = problem_set.problems.all()
    attempts = Attempt.objects.for_problem_set(problem_set).user_attempts(request.user)
    return render(request, "problem_set.html", {
        'courses': Course.user_courses(request.user),
        'problem_set': problem_set,
        'problems': problems,
        'all_courses': Course.objects.all(),
        'solved': ProblemSet.success(request.user),
        'teacher': user_is_teacher,
        'attempts': attempts,
        'languages': Language.objects
    })

def view_statistics(request, pk, limit):
    problem_set = get_object_or_404(ProblemSet, id=pk)
    verify(problem_set.course.has_teacher(request.user))
    attempts = dict((problem.id, {}) for problem in problem_set.problems.all())
    user_ids = set()
    limit = int(limit)
    success = dict((part.id, {'correct': 0, 'incorrect': 0}) for problem in problem_set.problems.all() for part in problem.parts.all())
    active_attempts = Attempt.objects.active().for_problem_set(problem_set)
    if limit:
        cutoff = datetime.datetime.now() - datetime.timedelta(minutes=limit)
        active_attempts = active_attempts.filter(submission__timestamp__gt=cutoff)
    for attempt in active_attempts.select_related('submission__user', 'part__problem_id'):
        user_id = attempt.submission.user_id
        user_ids.add(user_id)
        problem_id = attempt.part.problem_id
        user_attempts = attempts[problem_id].get(user_id, {})
        user_attempts[attempt.part_id] = attempt
        success[attempt.part_id]['correct' if attempt.correct else 'incorrect'] += 1 
        attempts[problem_id][user_id] = user_attempts
    limits = [
        ("Zadnje pol ure", 30),
        ("Zadnji dve uri", 2 * 60),
        ("Zadnji dan", 24 * 60),
        ("Zadnji teden", 7 * 24 * 60),
        ("Vse", 0)
    ]
    return render(request, "statistics.html", {
        'courses': Course.user_courses(request.user),
        'problem_set': problem_set,
        'users': User.objects.filter(id__in=user_ids).order_by('last_name'),
        'problems': problem_set.problems,
        'attempts': attempts,
        'solved': ProblemSet.success(request.user),
        'success': success,
        'limits': limits,
        'limit': limit,
        'teacher': True
    })


def results_zip(request, pk):
    problemset = get_object_or_404(ProblemSet, id=pk)
    verify(problemset.course.has_teacher(request.user))
    attempts = {}
    user_ids = set()
    active_attempts = Attempt.objects.active().for_problem_set(problemset)
    for attempt in active_attempts.select_related('submission__user_id'):
        user_id = attempt.submission.user_id
        user_ids.add(user_id)
        user_attempts = attempts.get(user_id, {})
        user_attempts[attempt.part_id] = attempt
        attempts[user_id] = user_attempts
    users = User.objects.filter(id__in=user_ids)
    archivename = "{0}-results".format(slugify(problemset.title))
    files = []
    for problem in problemset.problems.all():
        mass_template = problem.language.mass_file
        moss_template = problem.language.moss_file
        parts = problem.parts.all()
        for user in users.all():
            username = user.get_full_name() or user.username
            context = {
                'problem': problem,
                'preamble': problem.preamble_for(user),
                'parts': parts,
                'attempts': attempts[user.id],
                'user': user,
            }
            mass_filename = "{0}/{1}/{2}.{3}".format(archivename, slugify(problem.title), slugify(username), problem.language.extension)
            mass_contents = render_to_string(mass_template, context)
            files.append((mass_filename, mass_contents))
            moss_filename = "{0}/{1}-moss/{2}.{3}".format(archivename, slugify(problem.title), slugify(username), problem.language.extension)
            moss_contents = render_to_string(moss_template, context)
            files.append((moss_filename, moss_contents))
    context = {
        'problem_set': problemset,
        'users': User.objects.filter(id__in=user_ids).order_by('last_name'),
        'problems': [[part.id for part in problem.parts.all()] for problem in problemset.problems.all()],
        'attempts': attempts
    }
    filename = "{0}/{0}.csv".format(archivename)
    contents = render_to_string("results.csv",
                                context_instance=RequestContext(request, context))
    files.append((filename, contents))
    return zip_archive(archivename, files)


def student_zip(request, pk):
    problem_set = get_object_or_404(ProblemSet, id=pk)
    verify(problem_set.course.has_teacher(request.user) or problem_set.visible)
    archivename = slugify(problem_set.title)
    files = []
    for i, problem in enumerate(problem_set.problems.all()):
        filename = "{0}/{1:02d}-{2}".format(archivename, i + 1, problem.filename())
        contents = student_contents(request, problem, request.user,
                                    request.user.is_authenticated())
        files.append((filename, contents))
    return zip_archive(archivename, files)

def teacher_zip(request, pk):
    problem_set = get_object_or_404(ProblemSet, id=pk)
    verify(problem_set.course.has_teacher(request.user))
    archivename = "{0}-edit".format(slugify(problem_set.title))
    files = []
    for problem in problem_set.problems.all():
        filename = "{0}/{1}".format(archivename, problem.filename()) # Select your files here.
        contents = teacher_contents(request, problem, request.user)
        files.append((filename, contents))
    return zip_archive(archivename, files)

def create(request):
    verify(request.method == 'POST')
    course = get_object_or_404(Course, id=request.POST['course'])
    verify(course.has_teacher(request.user))
    problem_set = ProblemSet(course=course, title=request.POST['title'],
                             description=request.POST['description'],
                             visible=False, solution_visibility='pogojno')
    problem_set.save()
    return redirect(problem_set)


class ProblemSetDelete(DeleteView):
    model = ProblemSet
    success_url = reverse_lazy('tomo.views.homepage')

    def get_context_data(self, **kwargs):
        context = super(ProblemSetDelete, self).get_context_data(**kwargs)
        problems = self.object.problems.all()
        attempts = dict((problem.id, {}) for problem in problems)
        timestamps = dict((problem.id, {}) for problem in problems)
        user_ids = dict((problem.id, set()) for problem in problems)
        sorted_attempts = dict((problem.id, []) for problem in problems)
        active_attempts = Attempt.objects.active().for_problem_set(self.object)
        exists = False
        for attempt in active_attempts.select_related('submission__user_id', 'submission__timestamp', 'part__problem_id'):
            exists = True
            user_id = attempt.submission.user_id
            problem_id = attempt.part.problem_id
            user_ids[problem_id].add(user_id)
            user_attempts = attempts[problem_id].get(user_id, {})
            user_attempts[attempt.part_id] = attempt
            attempts[problem_id][user_id] = user_attempts
            timestamps[problem_id][user_id] = attempt.submission.timestamp
        for problem in problems:
            parts = problem.parts.all()
            for user in User.objects.filter(id__in=user_ids[problem.id]).order_by('last_name'):
                sorted_attempts[problem.id].append((user, timestamps[problem.id][user.id], [attempts[problem.id][user.id].get(part.id) for part in parts]))
        context['attempts'] = [(problem, sorted_attempts[problem.id]) for problem in problems]
        context['exists'] = exists
        return context


class ProblemSetCreate(CreateView):
    model = ProblemSet
    fields = ['title', 'description', 'visible', 'solution_visibility']

    def get_context_data(self, **kwargs):
        context = super(ProblemSetCreate, self).get_context_data(**kwargs)
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        context['course'] = course
        return context

    def form_valid(self, form):
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        form.instance.author = self.request.user
        form.instance.course = course
        verify(course.has_teacher(self.request.user))
        return super(ProblemSetCreate, self).form_valid(form)


class ProblemSetUpdate(UpdateView):
    model = ProblemSet
    fields = ['title', 'description', 'visible', 'solution_visibility']

    def get_object(self, *args, **kwargs):
        obj = super(ProblemSetUpdate, self).get_object(*args, **kwargs)
        verify(obj.course.has_teacher(self.request.user))
        return obj

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(ProblemSetUpdate, self).form_valid(form)



