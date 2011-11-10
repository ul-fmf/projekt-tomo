from django.shortcuts import get_object_or_404, render

from tomo.models import Course, Part, ProblemSet


def homepage(request):
    # TODO: Once we implement a view to select courses, enable the selection
    # if request.user.is_authenticated():
    #     courses = request.user.courses
    # else:
    #     courses = Course.objects
    courses = Course.objects
    return render(request, "home.html", {
        'courses': courses,
        'solved': ProblemSet.objects.problem_sets_success(ProblemSet.objects, request.user),
    })

def view_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, "course.html", {
        'course': course,
        'solved': ProblemSet.objects.problem_sets_success(ProblemSet.objects.filter(course=course), request.user),
    })
