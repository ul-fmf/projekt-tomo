from django.shortcuts import get_object_or_404, render, redirect

from courses.models import Course, ProblemSet


def homepage(request):
    return render(request, "home.html", {
        'courses': Course.user_courses(request.user),
        'all_courses': Course.objects.all(),
        'solved': ProblemSet.success(request.user),
    })

def settings(request):
    if request.method == "POST":
        request.user.courses = Course.objects.filter(id__in=request.POST.getlist('my_courses'))
        request.user.save()
    return redirect('homepage')
