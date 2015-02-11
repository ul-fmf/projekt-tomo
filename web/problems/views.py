from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.core.files import File
import zipfile
import StringIO

from problems.models import Problem, Part
from utils.views import plain_text


def problem_list(request):
    """Show basic template (index.html) """ 
    problem_list = Problem.objects.all()
    context = {'problem_list':problem_list}
    return render(request, 'problems/problem_list.html', context)
# Create your views here.


#TODO: create a file from problem data and serve that file to user
# 1.step: get data: problem title, problem description, part description, part solution, part validation, part secret
# 2.step: create  a new file and write all the data in it
# 3.step: make file downloadable
def problem_detail(request, problem_id):
    """ Show assignment details like description and parts"""
    problem = Problem.objects.get(pk=problem_id)
    context = {'problem': problem}
    return render(request, 'problems/problem_detail.html', context)

def return_problem_file(request, problem_id):
    problem = Problem.objects.get(pk=problem_id)
    user = request.user if request.user.is_authenticated() else None
    filename, contents = problem.attempt_file(user)
    return plain_text(filename, contents)

