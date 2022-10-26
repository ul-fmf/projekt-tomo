from django.urls import path, register_converter

from . import views
from .converters import TrueIntConverter
from .views import ProblemCreate, ProblemDelete, ProblemUpdate

register_converter(TrueIntConverter, "trueint")


urlpatterns = [
    path(
        "<int:problem_pk>/solutions/<int:user_pk>",
        views.problem_solution,
        name="problem_solution",
    ),
    path(
        "<int:problem_pk>/download/",
        views.problem_attempt_file,
        name="problem_attempt_file",
    ),
    path(
        "<int:problem_pk>/edit/",
        views.problem_edit_file,
        name="problem_edit_file",
    ),
    path(
        "<int:problem_pk>/move/<trueint:shift>/",
        views.problem_move,
        name="problem_move",
    ),
    path("<int:pk>/update/", ProblemUpdate.as_view(), name="problem_update"),
    path(
        "create/<int:problem_set_id>/",
        ProblemCreate.as_view(),
        name="problem_create",
    ),
    path(r"<int:pk>/delete/", ProblemDelete.as_view(), name="problem_delete"),
    path(r"<int:problem_pk>/copy/", views.copy_form, name="problem_copy"),
]
