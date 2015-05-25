from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from rest_framework.reverse import reverse
from problems.models import Problem
from attempts.models import Attempt
from courses.models import ProblemSet
from utils.views import plain_text
from utils import verify


@login_required
def problem_attempt_file(request, problem_pk):
    """Download an attempt file for a given problem."""
    problem = get_object_or_404(Problem, pk=problem_pk)
    verify(request.user.can_view_problem(problem))
    url = reverse('attempt-submit', request=request)
    filename, contents = problem.attempt_file(url, user=request.user)
    return plain_text(filename, contents)


@login_required
def problem_edit_file(request, problem_pk):
    """Download an attempt file for a given problem."""
    problem = get_object_or_404(Problem, pk=problem_pk)
    verify(request.user.can_edit_problem(problem))
    url = reverse('problem-submit', request=request)
    filename, contents = problem.edit_file(url, user=request.user)
    return plain_text(filename, contents)


def problem_move(request, problem_pk, shift):
    problem = get_object_or_404(Problem, pk=problem_pk)
    verify(request.user.can_edit_problem_set(problem.problem_set))
    problem.move(shift)
    return redirect(problem)


class ProblemCreate(CreateView):
    model = Problem
    fields = ['title', 'description']

    def get_context_data(self, **kwargs):
        context = super(ProblemCreate, self).get_context_data(**kwargs)
        problem_set = get_object_or_404(ProblemSet, id=self.kwargs['problem_set_id'])
        verify(self.request.user.can_edit_problem_set(problem_set))
        context['problem_set'] = problem_set
        return context

    def form_valid(self, form):
        problem_set = get_object_or_404(ProblemSet, id=self.kwargs['problem_set_id'])
        verify(self.request.user.can_edit_problem_set(problem_set))
        form.instance.author = self.request.user
        form.instance.problem_set = problem_set
        return super(ProblemCreate, self).form_valid(form)


class ProblemUpdate(UpdateView):
    model = Problem
    fields = ['title', 'description']

    def get_object(self, *args, **kwargs):
        obj = super(ProblemUpdate, self).get_object(*args, **kwargs)
        verify(self.request.user.can_edit_problem(obj))
        return obj

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(ProblemUpdate, self).form_valid(form)

# 
# class ProblemDelete(DeleteView):
#     '''
#         Delete a problem and all it's parts and attempts.
#     '''
#     model = Problem
#     def get_success_url(self):
#         return self.object.problem_set.get_absolute_url()
#  
#     def get_object(self, *args, **kwargs):
#         obj = super(ProblemDelete, self).get_object(*args, **kwargs)
#         verify(self.request.user.can_edit_problem(obj))
#         return obj
#  
#     def get_context_data(self, **kwargs):
#         context = super(ProblemDelete, self).get_context_data(**kwargs)
#         attempts = {}
#         submissions = {}
#         user_ids = set()
#         active_attempts = Attempt.objects.active().for_problem(self.object)
#         for attempt in active_attempts.select_related('submission__user'):
#             user_id = attempt.submission.user_id
#             user_ids.add(user_id)
#             user_attempts = attempts.get(user_id, {})
#             user_attempts[attempt.part_id] = attempt
#             attempts[user_id] = user_attempts
#             submissions[user_id] = attempt.submission
#         parts = self.object.parts.all()
#         sorted_attempts = []
#         for user in User.objects.filter(id__in=user_ids).order_by('last_name'):
#             sorted_attempts.append((user, submissions[user.id], [attempts[user.id].get(part.id) for part in parts]))
#         context['attempts'] = sorted_attempts
#         return context


#teacher status required
#TODO: problem_copy - to copy a problem

@login_required
def problem_solution(request, problem_pk):
    """Show problem solution."""
    problem = Problem.objects.get(pk=problem_pk)
    problem_set = problem.problem_set
    attempts = request.user.attempts.filter(part__problem__id=problem_pk)
    parts = problem.parts.all()
    
    
    for part in parts:
        try:
            part.attempt = attempts.get(part=part)
        except:
            part.attempt = None
    return render(request, 'problems/solutions.html', {
       'parts': parts,
       'problem_set': problem_set,
       'is_teacher': request.user.can_edit_problem_set(problem_set),
    })