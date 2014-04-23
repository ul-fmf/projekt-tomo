from django.contrib import admin
from .models import Submission, Attempt


class AttemptInline(admin.TabularInline):
    model = Attempt
    extra = 0


class SubmissionAdmin(admin.ModelAdmin):
    inlines = (
        AttemptInline,
    )
    date_hierarchy = 'timestamp'
    list_display = (
        'timestamp',
        'user',
        'course',
        'problem_set',
        'problem',
    )
    list_filter = (
        'problem__problem_set__course',
    )
    search_fields = (
        'user__username',
        'problem__title',
        'problem__problem_set__title',
    )

    def course(self, obj):
        return obj.problem.problem_set.course
    course.admin_order_field = 'problem__problem_set__course'

    def problem_set(self, obj):
        return obj.problem.problem_set
    problem_set.admin_order_field = 'problem__problem_set'

admin.site.register(Submission, SubmissionAdmin)
