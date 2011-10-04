from django.contrib import admin

from tomo.course.models import Course, ProblemSet
from tomo.problem.models import Problem

class ProblemSetInline(admin.StackedInline):
    model = ProblemSet
    extra = 0

class ProblemInline(admin.StackedInline):
    model = Problem
    extra = 0

class CourseAdmin(admin.ModelAdmin):
    inlines = [ProblemSetInline]
    list_display = ('shortname', 'name')
    list_editable = ('name', )
    save_on_top = True

class ProblemSetAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'description', ('visible', 'solution_visibility'))
        }),
    )
    inlines = [ProblemInline]
    list_display = ('title', 'visible', 'solution_visibility')
    list_filter = ('visible', 'solution_visibility')
    list_editable = ('visible', 'solution_visibility')
    save_on_top = True
    search_fields = ('problems__title', 'title', 'description')


admin.site.register(Course, CourseAdmin)
admin.site.register(ProblemSet, ProblemSetAdmin)
