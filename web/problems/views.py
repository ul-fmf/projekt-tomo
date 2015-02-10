from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.core.files import File
import zipfile
import StringIO

from problems.models import Problem, Part


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
    content = problem.attempt_file(request.user)
    zip_filename = "problem_{0}.zip".format(problem.id)
    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()
    # The zip compressor
    zf = zipfile.ZipFile(s, "w")
    zf.writestr("problem_{0}.py".format(problem.id), content.encode("utf-8"))
    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp
