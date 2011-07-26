from django.contrib import admin

from tomo.problem.models import Collection, Problem, Part, Solution, Submission


class PartInline(admin.StackedInline):
    model = Part

class ProblemAdmin(admin.ModelAdmin):
    inlines = [PartInline]

class SolutionInline(admin.StackedInline):
    model = Solution

class SubmissionAdmin(admin.ModelAdmin):
    inlines = [SolutionInline]

admin.site.register(Problem, ProblemAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Collection)
