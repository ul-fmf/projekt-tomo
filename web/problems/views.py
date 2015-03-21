from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.reverse import reverse
from problems.models import Problem
from utils.views import plain_text


@login_required
def problem_attempt_file(request, problem_pk):
    """Download an attempt file for a given problem."""
    problem = get_object_or_404(Problem, pk=problem_pk)
    user = request.user if request.user.is_authenticated() else None
    url = reverse('attempt-submit', request=request)
    filename, contents = problem.attempt_file(url, user=user)
    return plain_text(filename, contents)


@staff_member_required
def problem_edit_file(request, problem_pk):
    """Download an attempt file for a given problem."""
    problem = get_object_or_404(Problem, pk=problem_pk)
    user = request.user if request.user.is_authenticated() else None
    url = reverse('problem-submit', request=request)
    filename, contents = problem.edit_file(url, user=user)
    return plain_text(filename, contents)


@login_required
def problem_solution(request, problem_pk):
    """Show problem solution."""
    problem = Problem.objects.get(pk=problem_pk)
    parts = problem.parts.all()
    attempts = request.user.attempts.filter(part__problem__id=problem_pk)
    part_attempt = {}

    for part in parts:
        part_attempt[part] = attempts.filter(part=part)
    return render(request, 'problems/solutions.html', {'part_attempt': part_attempt})
