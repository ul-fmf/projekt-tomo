from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Attempt


class AttemptAdmin(SimpleHistoryAdmin):
    fields = [
        "user",
        "part",
        "problem",
        "problem_instance",
        "solution",
        "valid",
        "feedback",
    ]

    list_display = (
        "user",
        "problem",
        "problem_instance",
        "part",
        "valid",
    )
    list_filter = (
        "part__problem__problem_set__course__institution",
        "part__problem__problem_set__course",
        "part__problem__problem_set",
        "part__problem__visible",
    )
    search_fields = (
        "part__pk",
        "problem__problem_set__title",
        "problem__title",
        "user__username",
        "part__description",
    )
    date_hierarchy = "submission_date"

    readonly_fields = [
        "problem",
        "problem_instance",
    ]

    def problem(self, obj):
        return obj.part.problem

    problem.admin_order_field = "part__problem"


admin.site.register(Attempt, AttemptAdmin)
