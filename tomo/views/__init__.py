from django.shortcuts import get_object_or_404, render, redirect

from tomo.models import Course, ProblemSet
from tomo.forms import SettingsForm


def homepage(request):
    if request.user.is_authenticated():
        courses = request.user.courses
    else:
        courses = Course.objects
    return render(request, "home.html", {
        'courses': courses,
        'solved': ProblemSet.objects.success(request.user),
    })

def view_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, "course.html", {
        'course': course,
        'solved': ProblemSet.objects.filter(course=course).success(request.user)
    })

def settings(request):
    if request.method == "POST":
        request.user.courses = Course.objects.filter(id__in=request.POST.getlist('my_courses'))
        request.user.save()
        return redirect('homepage')
    return render(request, "settings.html", {
        'all_courses': Course.objects.all(),
        'my_courses': request.user.courses.all()
    })
