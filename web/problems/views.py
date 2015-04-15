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
    url = reverse('attempt-submit', request=request)
    filename, contents = problem.attempt_file(url, user=request.user)
    return plain_text(filename, contents)


@staff_member_required
def problem_edit_file(request, problem_pk):
    """Download an attempt file for a given problem."""
    problem = get_object_or_404(Problem, pk=problem_pk)
    url = reverse('problem-submit', request=request)
    filename, contents = problem.edit_file(url, user=request.user)
    return plain_text(filename, contents)


@login_required
def problem_solution(request, problem_pk):
    """Show problem solution."""
    problem = Problem.objects.get(pk=problem_pk)
    attempts = request.user.attempts.filter(part__problem__id=problem_pk)
    parts = problem.parts.all()

    for part in parts:
        try:
            part.attempt = attempts.get(part=part)
        except:
            part.attempt = None
    return render(request, 'problems/solutions.html', {'parts': parts})
