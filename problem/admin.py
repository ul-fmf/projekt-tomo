from django.contrib import admin

from tomo.problem.models import Problem, Part, Submission, Attempt


class PartInline(admin.StackedInline):
    model = Part
    extra = 0

class ProblemAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (('problem_set', 'title', 'author'), 'description')
        }),
        ('Source', {
            'classes': ('collapse', ),
            'fields': ('preamble', )
        }),
    )
    date_hierarchy = 'timestamp'
    inlines = [PartInline]
    list_display = ('title', 'problem_set', 'author')
    list_editable = ('problem_set', 'author')
    save_on_top = True
    search_fields = ('author__username', 'title', 'description')

class AttemptInline(admin.TabularInline):
    model = Attempt
    readonly_fields = ("part", "submission")
    extra = 0

class SubmissionAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    fieldsets = (
        (None, {
            'fields': (('user', 'problem'), )
        }),
        ('Source', {
            'classes': ('collapse', ),
            'fields': ('source', )
        })
    )
    inlines = [AttemptInline]
    list_display = ('timestamp', 'user', 'problem')
    list_filter = ('problem', 'timestamp')
    save_on_top = True
    search_fields = ['user__username', 'problem__title']


admin.site.register(Problem, ProblemAdmin)
admin.site.register(Submission, SubmissionAdmin)
