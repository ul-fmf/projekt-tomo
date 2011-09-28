from django.contrib import admin

from tomo.problem.models import Problem, Part, Submission, Attempt


class PartInline(admin.StackedInline):
    model = Part
    readonly_fields = ("problem", )
    extra = 0

class ProblemAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (('title', 'revealed', 'author'), 'description')
        }),
        ('Source', {
            'classes': ('collapse', ),
            'fields': ('preamble', )
        })
    )
    inlines = [PartInline]
    list_display = ('title', 'revealed', 'author')
    list_filter = ('revealed', )
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
