# -*- coding: utf-8 -*-
import hashlib, json, os

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response, redirect, render
from django.template import loader, Context, RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import csrf_exempt

from tomo.problem.views.download import *
from tomo.problem.models import *


def view_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    solved = dict((problem_set.id, problem_set.solved(request.user))
                  for problem_set in course.problem_sets.all())
    return render(request, "course.html", {
        'course': course,
        'solved': solved,
    })



