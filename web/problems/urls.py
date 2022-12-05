from django.urls import include, path, register_converter

from . import views
from .converters import TrueIntConverter
from .views import ProblemCreate, ProblemDelete, ProblemUpdate

register_converter(TrueIntConverter, "trueint")


urlpatterns = [
    path(
        "create/",
        ProblemCreate.as_view(),
        name="problem_create",
    ),
    path(
        "<int:problem_pk>/",
        include(
            [
                path(
                    "solutions/<int:user_pk>",
                    views.problem_solution,
                    name="problem_solution",
                ),
                path(
                    "download/",
                    views.problem_attempt_file,
                    name="problem_attempt_file",
                ),
                path(
                    "edit/",
                    views.problem_edit_file,
                    name="problem_edit_file",
                ),
                path(
                    "move/<trueint:shift>/",
                    views.problem_move,
                    name="problem_move",
                ),
                path("update/", ProblemUpdate.as_view(), name="problem_update"),
                path("delete/", ProblemDelete.as_view(), name="problem_delete"),
                path("copy/", views.copy_form, name="problem_copy"),
            ]
        ),
    ),
]
