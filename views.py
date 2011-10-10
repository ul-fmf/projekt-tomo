from django.shortcuts import render

from tomo.course.models import Course

def homepage(request):
    # TODO: Once we implement a view to select courses, enable the selection
    # if request.user.is_authenticated():
    #     courses = request.user.courses
    # else:
    #     courses = Course.objects
    courses = Course.objects
    solved = dict((problem_set.id, problem_set.solved(request.user))
                    for course in courses.all()
                    for problem_set in course.recent())
    return render(request, "home.html", {
        'courses': courses,
        'solved': solved,
    })
