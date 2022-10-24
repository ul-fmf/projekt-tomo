from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Part, Problem


class PartInline(admin.StackedInline):
    model = Part
    extra = 0


class ProblemAdmin(SimpleHistoryAdmin):
    inlines = (PartInline,)
    list_display = (
        "course",
        "problem_set",
        "title",
        "description",
    )
    list_display_links = ("title",)
    ordering = (
        "problem_set__course",
        "problem_set",
        "_order",
    )
    search_fields = (
        "title",
        "description",
    )

    def course(self, obj):
        return obj.problem_set.course

    course.admin_order_field = "problem_set__course"


admin.site.register(Problem, ProblemAdmin)
