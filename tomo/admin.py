from django.contrib import admin

from tomo.models import Language, Problem, Part, Submission, Attempt, ProblemSet, Course

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
    list_display = ('title', 'problem_set', 'author', 'language', 'timestamp')
    list_editable = ('problem_set', 'author', 'language')
    list_filter = ('author', 'language', 'problem_set')
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
            'fields': (('user', 'problem', 'ip'), )
        }),
        ('Source', {
            'classes': ('collapse', ),
            'fields': ('preamble', 'source', )
        })
    )
    inlines = [AttemptInline]
    list_display = ('timestamp', 'user', 'problem')
    list_filter = ('problem', 'timestamp')
    save_on_top = True
    search_fields = ['user__username', 'problem__title']

class ProblemSetInline(admin.StackedInline):
    model = ProblemSet
    extra = 0

class ProblemInline(admin.StackedInline):
    model = Problem
    extra = 0

class CourseAdmin(admin.ModelAdmin):
    inlines = [ProblemSetInline]
    list_display = ('shortname', 'name', 'timestamp')
    list_editable = ('name', )
    save_on_top = True

class PartAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'timestamp',)

class ProblemSetAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'description', ('visible', 'solution_visibility'))
        }),
    )
    inlines = [ProblemInline]
    list_display = ('title', 'visible', 'solution_visibility', 'timestamp')
    list_filter = ('visible', 'solution_visibility')
    list_editable = ('visible', 'solution_visibility')
    save_on_top = True
    search_fields = ('problems__title', 'title', 'description')


admin.site.register(Course, CourseAdmin)
admin.site.register(ProblemSet, ProblemSetAdmin)
admin.site.register(Language)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Part, PartAdmin)
