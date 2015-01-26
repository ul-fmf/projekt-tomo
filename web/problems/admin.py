from django.contrib import admin
from .models import Problem, Part


admin.site.register([Problem, Part])
