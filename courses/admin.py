from django.contrib import admin
from courses.models import ProblemSet, Course

admin.site.register(Course)
admin.site.register(ProblemSet)
