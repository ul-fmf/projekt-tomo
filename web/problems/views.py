from django.shortcuts import get_object_or_404, get_list_or_404, render
from problems.models import Problem, Part
from utils.views import plain_text
from django.http import HttpResponseRedirect
from django import forms


class Sign_In_Form(forms.Form):
    username = forms.CharField(max_length=40)
    password = forms.CharField(max_length=40)


def welcome(request):
    """
    Show welcome message and sign-in form.
    Validate send data.
    """
    if request.method == 'POST':  # If the form has been submitted ...
        # A form bound to the POST data:
        sign_in_form = Sign_In_Form(request.POST)
        if sign_in_form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # LDAP avtentikacija?

            # Redirect after POST - TODO: kasneje nastavi na 'my_courses'
            # oz. 'not_yet_enrolled'
            return HttpResponseRedirect('../problem_list/')
    else:
        sign_in_form = Sign_In_Form()  # An unbound form

    return render(request, 'problems/welcome.html', {
        'form': sign_in_form,
    })


def problem_list(request):
    """Show a list of all problems."""
    return render(request, 'problems/problem_list.html', {
        'problems': Problem.objects.all()
    })


#def problem_detail(request, problem_pk):
#    """Show problem details such as description and parts."""
#    problem = get_object_or_404(Problem, pk=problem_pk)
#    return render(request, 'problems/problem_detail.html', {
#        'problem': problem
#    })


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
    attempts = user.attempts(problem=problem_pk)
    part_attempt = {}

    for part in parts:
        part_attempt[part] = attempts.filter(part=part)
    return render(request, 'problems/solution.html', part_attempt)
