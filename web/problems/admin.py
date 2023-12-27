from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Part, Problem


class PartInline(admin.StackedInline):
    model = Part
    extra = 0


class ProblemAdmin(SimpleHistoryAdmin):
    inlines = (PartInline,)
    list_display = (
        "title",
        "description",
    )
    list_display_links = ("title",)
    ordering = (
        "title",
    )
    search_fields = (
        "title",
        "description",
    )

    list_filter = (
        "language",
    )


admin.site.register(Problem, ProblemAdmin)
