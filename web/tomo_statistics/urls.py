from django.urls import path

from . import views

urlpatterns = [
    path("<int:course_pk>", views.course_statistics, name="statistics_landing_page"),
    path(
        "<int:course_pk>/submission_history",
        views.course_submission_history,
        name="statistics_submission_history",
    ),
    path(
        "<int:course_pk>/submission_history/<int:problemset_pk>",
        views.course_submission_history_problemset,
        name="statistics_submission_history_problemset",
    ),
    path(
        "<int:course_pk>/submission_history/<int:problemset_pk>/<int:student_pk>",
        views.course_user_submission_history_problemset,
        name="statistics_submission_history_problemset_user",
    ),
    path(
        "historical_attempt/<int:historical_attempt_pk>",
        views.user_problem_solution_at_time,
        name="user_problem_solution_at_time",
    ),
    path(
        "<int:student_pk>/<int:part_pk>",
        views.user_problem_solution_through_time,
        name="user_problem_solution_through_time",
    ),
    path("<int:course_pk>/compare", views.compare_solutions, name="compare_solutions"),
    path("", views.main_view, name="main_view"),
    path("<int:course_pk>/", views.test_view, name="test_view"),
    path("graf_test/<int:course_pk>/", views.graph, name="graph"),
    path("<int:course_pk>/", views.course_graphs, name="course_graphs"),
    path("<int:course_pk>/users", views.user_success, name="user_success"),
    path("<int:course_pk>/js", views.graph_json, name="graph_json"),
    path(
        "<int:course_pk>/active/<int:days>",
        views.course_graphs_active,
        name="course_graphs_active",
    ),
]
