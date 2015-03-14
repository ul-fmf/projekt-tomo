from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Problem, Part


class PartInline(admin.StackedInline):
    model = Part
    extra = 0


class ProblemAdmin(SimpleHistoryAdmin):
    inlines = (
        PartInline,
    )
    list_display = (
        'title',
        'description',
    )
    list_display_links = (
        'title',
    )
    search_fields = (
        'title',
        'description',
    )


admin.site.register(Problem, ProblemAdmin)
