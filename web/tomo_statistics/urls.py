from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(
        r"^(?P<course_pk>\d+)$", views.course_statistics, name="statistics_landing_page"
    ),
    url(
        r"^(?P<course_pk>\d+)/submission_history$",
        views.course_submission_history,
        name="statistics_submission_history",
    ),
    url(
        r"^(?P<course_pk>\d+)/submission_history/(?P<problemset_pk>\d+)$",
        views.course_submission_history_problemset,
        name="statistics_submission_history_problemset",
    ),
    url(
        r"^(?P<course_pk>\d+)/submission_history/(?P<problemset_pk>\d+)/(?P<student_pk>\d+)$",
        views.course_user_submission_history_problemset,
        name="statistics_submission_history_problemset_user",
    ),
    url(
        r"^historical_attempt/(?P<historical_attempt_pk>\d+)$",
        views.user_problem_solution_at_time,
        name="user_problem_solution_at_time",
    ),
    url(
        r"^(?P<student_pk>\d+)/(?P<part_pk>\d+)$",
        views.user_problem_solution_through_time,
        name="user_problem_solution_through_time",
    ),
]
