from django.conf.urls import include, url

from . import views

urlpatterns = [
    url("<int:course_pk>", views.course_statistics, name="statistics_landing_page"),
    url(
        "<int:course_pk>/submission_history",
        views.course_submission_history,
        name="statistics_submission_history",
    ),
    url(
        "<int:course_pk>/submission_history/<int:problemset_pk>",
        views.course_submission_history_problemset,
        name="statistics_submission_history_problemset",
    ),
    url(
        "<int:course_pk>/submission_history/<int:problemset_pk>/<int:student_pk>",
        views.course_user_submission_history_problemset,
        name="statistics_submission_history_problemset_user",
    ),
    url(
        "historical_attempt/<int:historical_attempt_pk>",
        views.user_problem_solution_at_time,
        name="user_problem_solution_at_time",
    ),
    url(
        "<int:student_pk>/<int:part_pk>",
        views.user_problem_solution_through_time,
        name="user_problem_solution_through_time",
    ),
]
