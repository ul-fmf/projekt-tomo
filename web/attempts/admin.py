from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Attempt


class AttemptAdmin(SimpleHistoryAdmin):
    fields = [
        "user",
        "part",
        "problem_instance",
        "solution",
        "valid",
        "feedback",
    ]

    list_display = (
        "user",
        "problem_instance",
        "part",
        "valid",
    )
    list_filter = (
        "problem_instance__problem_set__course__institution",
        "problem_instance__problem_set__course",
        "problem_instance__problem_set",
        "problem_instance__visible",
    )
    search_fields = (
        "part__pk",
        "problem_instance__problem_set__title",
        "problem_instance__problem__title",
        "user__username",
        "part__description",
    )
    date_hierarchy = "submission_date"

    readonly_fields = [
        "problem_instance",
    ]

    def problem(self, obj):
        return obj.part.problem

    problem.admin_order_field = "part__problem"


admin.site.register(Attempt, AttemptAdmin)
