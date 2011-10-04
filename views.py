from django.shortcuts import render

from tomo.course.models import Course

def homepage(request):
    if request.user.is_authenticated():
        courses = request.user.courses
    else:
        courses = Course.objects
    solved = dict((problem_set.id, problem_set.solved(request.user))
                    for course in courses.all()
                    for problem_set in course.recent())
    return render(request, "home.html", {
        'courses': courses,
        'solved': solved,
    })
