from django.urls import path, include

from . import views
from .views import ProblemSetCreate, ProblemSetDelete, ProblemSetUpdate

problem_set_urls = [
    path(
        "",
        views.problem_set_detail,
        name="problem_set_detail",
    ),
    path(
        "download/",
        views.problem_set_attempts,
        name="problem_set_attempts",
    ),
    path(
        "static/",
        views.problem_set_static,
        name="problem_set_static",
    ),
    path(
        "izpit/",
        views.problem_set_izpit,
        name="problem_set_izpit",
    ),
    path(
        "tex/",
        views.problem_set_tex,
        name="problem_set_tex",
    ),
    path(
        "edit/",
        views.problem_set_edit,
        name="problem_set_edit",
    ),
    path(
        "results/",
        views.problem_set_results,
        name="problem_set_results",
    ),
    path(
        "move/",
        views.problem_set_move,
        name="problem_set_move",
    ),
    path(
        "toggle_visible/",
        views.problem_set_toggle_visible,
        name="problem_set_toggle_visible",
    ),
    path(
        "toggle_solution_visibility/",
        views.problem_set_toggle_solution_visibility,
        name="problem_set_toggle_solution_visibility",
    ),
    path(
        "progress/",
        views.problem_set_progress,
        name="problem_set_progress",
    ),
    path(
        "progress/groups/<int:group_pk>",
        views.problem_set_progress_groups,
        name="problem_set_progress_groups",
    ),

]

course_urls = [
    path("", views.course_detail, name="course_detail"),
    path(
        "enroll_in_course/",
        views.enroll_in_course,
        name="enroll_in_course",
    ),
    path(
        "unenroll_from_course/",
        views.unenroll_from_course,
        name="unenroll_from_course",
    ),
    path(
        "<int:teacher_pk>/demote_to_student",
        views.demote_to_student,
        name="demote_to_student",
    ),
    path(
        "<int:student_pk>/promote_to_teacher",
        views.promote_to_teacher,
        name="promote_to_teacher",
    ),
    path(
        "<int:student_pk>/toggle_observed",
        views.toggle_observed,
        name="toggle_observed",
    ),
    path(
        "progress/<int:user_pk>/",
        views.course_progress,
        name="course_progress",
    ),
    path(
        "create_problem_set/",
        ProblemSetCreate.as_view(),
        name="problem_set_create",
    ),
    path(
        "update_problem_set/",
        ProblemSetUpdate.as_view(),
        name="problem_set_update",
    ),
    path(
        "delete_problem_set/",
        ProblemSetDelete.as_view(),
        name="problem_set_delete",
    ),
    path(
        "groups/",
        views.course_groups,
        name="course_groups",
    ),
    path(
        "groups/create/",
        views.course_groups_create,
        name="course_groups_create",
    ),
]

groups_urls = [
    path(
        "update/",
        views.course_groups_update,
        name="course_groups_update",
    ),
    path(
        "delete",
        views.course_groups_delete,
        name="course_groups_delete",
    ),
    path(
        "confirm_delete",
        views.course_groups_confirm_delete,
        name="course_groups_confirm_delete",
    ),
]

urlpatterns = [
    path("problem_set/<int:problem_set_pk>/", include(problem_set_urls)),
    path("course/<int:course_pk>/", include(course_urls)),
    path("groups/<int:group_pk>/", include(groups_urls)),
]
