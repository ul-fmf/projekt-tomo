from django.shortcuts import get_object_or_404, render

from tomo.problem.models import Course


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

def view_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    solved = dict((problem_set.id, problem_set.solved(request.user))
                  for problem_set in course.problem_sets.all())
    return render(request, "course.html", {
        'course': course,
        'solved': solved,
    })
