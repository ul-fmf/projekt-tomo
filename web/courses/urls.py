from django.urls import path, include

from . import views
from .views import ProblemSetCreate, ProblemSetDelete, ProblemSetUpdate

problem_set_urls = [
    path(
        "<int:problem_set_pk>/",
        views.problem_set_detail,
        name="problem_set_detail",
    ),
    path(
        "<int:problem_set_pk>/download/",
        views.problem_set_attempts,
        name="problem_set_attempts",
    ),
    path(
        "<int:problem_set_pk>/static/",
        views.problem_set_static,
        name="problem_set_static",
    ),
    path(
        "<int:problem_set_pk>/izpit/",
        views.problem_set_izpit,
        name="problem_set_izpit",
    ),
    path(
        "<int:problem_set_pk>/tex/",
        views.problem_set_tex,
        name="problem_set_tex",
    ),
    path(
        "<int:problem_set_pk>/edit/",
        views.problem_set_edit,
        name="problem_set_edit",
    ),
    path(
        "<int:problem_set_pk>/results/",
        views.problem_set_results,
        name="problem_set_results",
    ),
    path(
        "<int:problem_set_pk>/move/",
        views.problem_set_move,
        name="problem_set_move",
    ),
    path(
        "<int:problem_set_pk>/toggle_visible/",
        views.problem_set_toggle_visible,
        name="problem_set_toggle_visible",
    ),
    path(
        "<int:problem_set_pk>/toggle_solution_visibility/",
        views.problem_set_toggle_solution_visibility,
        name="problem_set_toggle_solution_visibility",
    ),
    path(
        "create/<int:course_pk>/",
        ProblemSetCreate.as_view(),
        name="problem_set_create",
    ),
    path(
        "<int:pk>/update/",
        ProblemSetUpdate.as_view(),
        name="problem_set_update",
    ),
    path(
        "<int:pk>/delete/",
        ProblemSetDelete.as_view(),
        name="problem_set_delete",
    ),
    path(
        "<int:problem_set_pk>/progress/",
        views.problem_set_progress,
        name="problem_set_progress",
    ),
    path(
        "<int:problem_set_pk>/progress/groups/<int:group_pk>",
        views.problem_set_progress_groups,
        name="problem_set_progress_groups",
    ),
]

course_urls = [
    path("<int:course_pk>/", views.course_detail, name="course_detail"),
    path(
        "<int:course_pk>/enroll_in_course/",
        views.enroll_in_course,
        name="enroll_in_course",
    ),
    path(
        "<int:course_pk>/unenroll_from_course/",
        views.unenroll_from_course,
        name="unenroll_from_course",
    ),
    path(
        "<int:course_pk>/<int:teacher_pk>/demote_to_student",
        views.demote_to_student,
        name="demote_to_student",
    ),
    path(
        "<int:course_pk>/<int:student_pk>/promote_to_teacher",
        views.promote_to_teacher,
        name="promote_to_teacher",
    ),
    path(
        "<int:course_pk>/<int:student_pk>/toggle_observed",
        views.toggle_observed,
        name="toggle_observed",
    ),
    path(
        "<int:course_pk>/progress/<int:user_pk>/",
        views.course_progress,
        name="course_progress",
    ),
    path(
        "<int:course_pk>/groups/",
        views.course_groups,
        name="course_groups",
    ),
    path(
        "<int:course_pk>/groups/create/",
        views.course_groups_create,
        name="course_groups_create",
    ),
]

groups_urls = [
    path(
        "<int:group_pk>/update/",
        views.course_groups_update,
        name="course_groups_update",
    ),
    path(
        "<int:group_pk>/delete",
        views.course_groups_delete,
        name="course_groups_delete",
    ),
    path(
        "<int:group_pk>/confirm_delete",
        views.course_groups_confirm_delete,
        name="course_groups_confirm_delete",
    ),
]

urlpatterns = [
    path("problem_set/", include(problem_set_urls)),
    path("course/", include(course_urls)),
    path("groups/", include(groups_urls)),
]
