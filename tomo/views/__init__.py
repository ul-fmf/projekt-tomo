from django.shortcuts import render, redirect
from courses.models import Course, ProblemSet


def homepage(request):
    return render(request, "home.html", {
        'courses': Course.user_courses(request.user),
        'all_courses': Course.objects.all(),
        'solved': ProblemSet.success(request.user),
    })
