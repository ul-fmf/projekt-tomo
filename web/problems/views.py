from django.shortcuts import get_object_or_404, render
from problems.models import Problem
from utils.views import plain_text


def problem_list(request):
    """Show a list of all problems."""
    return render(request, 'problems/problem_list.html', {
        'problems': Problem.objects.all()
    })


def problem_detail(request, problem_pk):
    """Show problem details such as description and parts."""
    problem = get_object_or_404(Problem, pk=problem_pk)
    return render(request, 'problems/problem_detail.html', {
        'problem': problem
    })


def problem_attempt_file(request, problem_pk):
    """Download an attempt file for a given problem."""
    problem = get_object_or_404(Problem, pk=problem_pk)
    user = request.user if request.user.is_authenticated() else None
    filename, contents = problem.attempt_file(user=user)
    return plain_text(filename, contents)
