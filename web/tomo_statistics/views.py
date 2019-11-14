from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from courses.models import Course, ProblemSet
from users.models import User
from utils import verify
from tomo_statistics.statistics_utils import get_submission_history

@login_required
def course_statistics(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_view_course_statistics(course))
    return render(request, 'statistics/contents.html', {'course' : course})

@login_required
def course_submission_history(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_view_course_statistics(course))
    return render(request, 'statistics/submission_history.html', {'course' : course})

@login_required
def course_submission_history_problemset(request, course_pk, problemset_pk):
    course = get_object_or_404(Course, pk=course_pk)
    problemset = get_object_or_404(ProblemSet, pk=problemset_pk)
    verify(request.user.can_view_course_statistics(course))
    return render(request, 'statistics/submission_history_problemset.html',
                {
                    'course' : course,
                    'problemset' : problemset
                })

@login_required
def course_user_submission_history_problemset(request, course_pk, problemset_pk, user_pk):
    course = get_object_or_404(Course, pk=course_pk)
    user = get_object_or_404(User, pk=user_pk)
    problemset = get_object_or_404(ProblemSet, pk=problemset_pk)
    verify(request.user.can_view_course_statistics(course))
    user_history = get_submission_history(problemset, user)
    return render(request,
                 "statistics/user_submission_history.html",
                {
                    'course' : course,
                    'problemset' : problemset,
                    'user' : user,
                    'history' : user_history
                })

