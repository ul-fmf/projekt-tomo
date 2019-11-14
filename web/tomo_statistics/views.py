from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from courses.models import Course
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
def course_user_submission_history(request, course_pk, user_pk):
    course = get_object_or_404(Course, pk=course_pk)
    user = get_object_or_404(User, pk=user_pk)
    verify(request.user.can_view_course_statistics(course))
    user_history = get_submission_history(course, user)
    return render(request,
                 "statistics/user_submission_history.html",
                {
                    'course' : course,
                    'user' : user,
                    'history' : user_history
                })

