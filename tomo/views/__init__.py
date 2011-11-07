from django.shortcuts import get_object_or_404, render

from tomo.models import Course, Part


def homepage(request):
    # TODO: Once we implement a view to select courses, enable the selection
    # if request.user.is_authenticated():
    #     courses = request.user.courses
    # else:
    #     courses = Course.objects
    courses = Course.objects
    sol = dict((problem_set.id, Part.solved(Part.objects.filter(problem__problem_set=problem_set), request.user))
                    for course in courses.all()
                    for problem_set in course.recent())
    return render(request, "home.html", {
        'courses': courses,
        'solved': sol,
    })

def view_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    solved = dict((problem_set.id, Part.solved(Part.objects.filter(problem__problem_set=problem_set), request.user))
                  for problem_set in course.problem_sets.all())
    return render(request, "course.html", {
        'course': course,
        'solved': solved,
    })
