from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.reverse import reverse
from .models import Course, ProblemSet
from utils.views import zip_archive


@login_required
def problem_set_attempts(request, problem_set_pk):
    """Download an archive of attempt files for a given problem set."""
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    user = request.user if request.user.is_authenticated() else None
    url = reverse('attempt-submit', request=request)
    archive_name, files = problem_set.attempts_archive(url, user)
    return zip_archive(archive_name, files)


@login_required
def problem_set_detail(request, problem_set_pk):
    """Show a list of all problems in a problem set."""
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)

    user_attempts = request.user.attempts.filter(part__problem__problem_set__id=problem_set_pk)
    valid_parts_ids = user_attempts.filter(valid=True).values_list('part_id', flat=True)
    invalid_parts_ids = user_attempts.filter(valid=False).values_list('part_id', flat=True)

    attempted_problems = problem_set.attempted_problems(request.user)
    valid_problems_ids = [problem.id for problem in problem_set.valid_problems(request.user)]
    invalid_problems_ids = [problem.id for problem in problem_set.invalid_problems(request.user)]

    half_valid_problems_ids = [problem.id for problem in attempted_problems
                               if problem.id not in valid_problems_ids
                               and problem.id not in invalid_problems_ids]

    return render(request, 'courses/problem_set_detail.html', {
        'problem_set': problem_set,
        'problems': problem_set.problems.all(),
        'valid_parts_ids': valid_parts_ids,
        'invalid_parts_ids': invalid_parts_ids,
        'valid_problems_ids': valid_problems_ids,
        'invalid_problems_ids': invalid_problems_ids,
        'half_valid_problems_ids': half_valid_problems_ids,
        'show_teacher_forms': request.user.teaches(problem_set.course),
    })


@login_required
def course_detail(request, course_pk):
    """Show a list of all problems in a problem set."""
    course = get_object_or_404(Course, pk=course_pk)
    course.annotated_problem_sets = list(course.problem_sets.all())
    for problem_set in course.annotated_problem_sets:
        problem_set.percentage = problem_set.valid_percentage(request.user)
    return render(request, 'courses/course_detail.html', {
        'course': course
    })


@login_required
def homepage(request):
    """Show a list of all problems in a problem set."""
    courses = Course.objects.all()
    for course in courses:
        course.annotated_problem_sets = list(course.recent_problem_sets())
        for problem_set in course.annotated_problem_sets:
            problem_set.percentage = problem_set.valid_percentage(request.user)
    return render(request, 'homepage.html', {
        'courses': courses
    })


@staff_member_required
def problem_set_move(request, problem_set_pk, shift):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    problem_set.move(shift)
    return redirect(problem_set.course)
