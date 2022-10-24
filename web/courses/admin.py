from django.contrib import admin

from .models import Course, CourseGroup, Institution, ProblemSet, StudentEnrollment


class StudentEnrollmentInline(admin.StackedInline):
    model = StudentEnrollment


class CourseAdmin(admin.ModelAdmin):
    filter_horizontal = (
        "teachers",
        "students",
    )
    inlines = (StudentEnrollmentInline,)
    list_filter = ("institution__name",)

    def podvoji(self, request, queryset):
        for course in queryset:
            course.duplicate()

    podvoji.short_description = "Podvoji"

    actions = [podvoji]


class ProblemSetAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "title",
    )
    list_display_links = ("title",)
    list_filter = ("course",)
    ordering = (
        "course",
        "_order",
    )
    search_fields = (
        "title",
        "description",
    )


class CourseGroupAdmin(admin.ModelAdmin):

    filter_horizontal = ("students",)


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    ordering = ("name",)
    search_fields = ("name",)


admin.site.register(Course, CourseAdmin)
admin.site.register(ProblemSet, ProblemSetAdmin)
admin.site.register(CourseGroup, CourseGroupAdmin)
admin.site.register(Institution, InstitutionAdmin)
