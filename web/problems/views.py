from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.contrib.auth import authenticate, login
from django import forms
from django.shortcuts import redirect
from django.forms.forms import NON_FIELD_ERRORS
from problems.models import Problem, Part
from utils.views import plain_text


class Sign_In_Form(forms.Form):
    username = forms.CharField(max_length=40, label='Uporabnisko ime')
    password = forms.CharField(widget=forms.PasswordInput, max_length=40, label='Geslo')


def welcome(request):
    """
    Show welcome message and sign-in form.
    Validate send data.
    """
    if request.user.is_authenticated():
        return redirect('problem_list')

    if request.method == 'POST':  # If the form has been submitted ...
        # A form bound to the POST data:
        sign_in_form = Sign_In_Form(request.POST)
        if sign_in_form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('problem_list')
                else:
                    # Return a 'disabled account' error message
                    sign_in_form.errors[NON_FIELD_ERRORS] = sign_in_form.error_class(["Account disabled"])
            else:
               sign_in_form.errors[NON_FIELD_ERRORS] = sign_in_form.error_class(["Invalid login"])
    else:
        sign_in_form = Sign_In_Form()  # An empty

    return render(request, 'problems/welcome.html', {
        'form': sign_in_form,
    })


@login_required
def problem_list(request):
    """Show a list of all problems."""
    user_attempts = request.user.attempts.all()
    valid_parts_ids = user_attempts.filter(valid=True).values_list('id', flat=True)
    invalid_parts_ids = user_attempts.filter(valid=False).values_list('id', flat=True)
    problems = Problem.objects.all()
    invalid_problems_ids = problems.filter(parts__id__in=invalid_parts_ids).values_list('id', flat=True)    
    valid_problems_ids = [p.id for p in problems
                          if p.parts.filter(id__in=valid_parts_ids).count() == p.parts.count() and p.parts.count() > 0]
    half_valid_problems_ids = problems.filter(parts__id__in=valid_parts_ids).exclude(id__in=valid_problems_ids).values_list('id', flat=True)

    return render(request, 'problems/problem_list.html', {
        'problems': Problem.objects.all(),
        'valid_parts_ids': valid_parts_ids,
        'invalid_parts_ids': invalid_parts_ids,
        'valid_problems_ids': valid_problems_ids,
        'invalid_problems_ids': invalid_problems_ids,
        'half_valid_problems_ids': half_valid_problems_ids,
    })


def problem_attempt_file(request, problem_pk):
    """Download an attempt file for a given problem."""
    problem = get_object_or_404(Problem, pk=problem_pk)
    user = request.user if request.user.is_authenticated() else None
    filename, contents = problem.attempt_file(user=user)
    return plain_text(filename, contents)


def problem_solution(request, problem_pk):
    """Show problem solution."""
    parts = get_list_or_404(Part, problem=problem_pk)
    user = request.user if request.user.is_authenticated() else None
    attempts = user.attempts.filter(part__problem__id=problem_pk)
    part_attempt = {}

    for part in parts:
        part_attempt[part] = attempts.filter(part=part)
    return render(request, 'problems/solutions.html', part_attempt)
