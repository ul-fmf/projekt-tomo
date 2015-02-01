from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
import zipfile
import StringIO

from problems.models import Problem, Part


def index(request):
    """Show basic template (index.html) """ 
    problem_list = Problem.objects.all()
    context = {'problem_list':problem_list}
    return render(request, 'problems/index.html', context)
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
    """ Create new file, write assignment data in it and return the file"""
    problem = Problem.objects.get(pk=problem_id)
    file_content = problem.title + '\n' + '\n' + problem.description
    #create temporary file (to save memory) and zip it
    buffer = StringIO.StringIO()
    problem_file = zipfile.ZipFile( buffer, "w" )
    problem_file.writestr("file1.txt", file_content)
    problem_file.close()
    #serve the file
    response = HttpResponse(buffer.getvalue(), mimetype='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename="'+problem.title+'.zip"'
    return response
    
