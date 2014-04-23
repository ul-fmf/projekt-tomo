from django.contrib import admin
from .models import Problem, Part


class PartInline(admin.StackedInline):
    model = Part
    extra = 0


class ProblemAdmin(admin.ModelAdmin):
    inlines = (
        PartInline,
    )
    list_filter = (
        'problem_set__course',
    )
    list_display = (
        'course',
        'problem_set',
        'title',
    )
    list_display_links = (
        'title',
    )
    ordering = (
        'problem_set__course',
        'problem_set',
    )
    search_fields = (
        'title',
        'problem_set__title',
        'description',
    )

    def course(self, obj):
        return obj.problem_set.course
    course.admin_order_field = 'problem_set__course'

admin.site.register(Problem, ProblemAdmin)
