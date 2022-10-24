from attempts.models import HistoricalAttempt
from courses.models import Course, ProblemSet
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from problems.models import Part
from tomo_statistics.statistics_utils import (
    append_time_differences_between_attempts,
    get_problem_solve_state_at_time,
    get_submission_history,
)
from users.models import User
from utils import verify


@login_required
def course_statistics(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_view_course_statistics(course))
    return render(request, "statistics/contents.html", {"course": course})


@login_required
def course_submission_history(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_view_course_statistics(course))
    return render(request, "statistics/submission_history.html", {"course": course})


@login_required
def course_submission_history_problemset(request, course_pk, problemset_pk):
    course = get_object_or_404(Course, pk=course_pk)
    problemset = get_object_or_404(ProblemSet, pk=problemset_pk)
    verify(request.user.can_view_course_statistics(course))
    return render(
        request,
        "statistics/submission_history_problemset.html",
        {"course": course, "problemset": problemset},
    )


@login_required
def course_user_submission_history_problemset(
    request, course_pk, problemset_pk, student_pk
):
    course = get_object_or_404(Course, pk=course_pk)
    student = get_object_or_404(User, pk=student_pk)
    problemset = get_object_or_404(ProblemSet, pk=problemset_pk)
    verify(request.user.can_view_course_statistics(course))
    user_history = get_submission_history(problemset, student)
    return render(
        request,
        "statistics/user_submission_history.html",
        {
            "course": course,
            "problemset": problemset,
            "student": student,
            "history": user_history,
        },
    )


@login_required
def user_problem_solution_at_time(request, historical_attempt_pk):
    historical_attempt = get_object_or_404(HistoricalAttempt, pk=historical_attempt_pk)
    problem = historical_attempt.part.problem
    course = problem.problem_set.course
    student = historical_attempt.user
    problem_state = get_problem_solve_state_at_time(historical_attempt)
    verify(request.user.can_view_course_statistics(course))
    return render(
        request,
        "statistics/solution_at_time.html",
        {
            "historical_attempt": historical_attempt,
            "problem": problem,
            "student": student,
            "parts": problem_state,
            "course": course,
            "show_teacher_forms": request.user.can_view_course_statistics(course),
        },
    )


@login_required
def user_problem_solution_through_time(request, student_pk, part_pk):
    student = get_object_or_404(User, pk=student_pk)
    part = get_object_or_404(Part, pk=part_pk)
    course = part.problem.problem_set.course
    user_part_attempts = list(
        HistoricalAttempt.objects.filter(part=part, user=student).reverse()
    )
    modified_attempts = append_time_differences_between_attempts(user_part_attempts)

    verify(request.user.can_view_course_statistics(course))
    return render(
        request,
        "statistics/user_problem_part_solution_history.html",
        {
            "student": student,
            "part": part,
            "course": course,
            "user_part_attempts": modified_attempts,
        },
    )
