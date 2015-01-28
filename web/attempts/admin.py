from django.contrib import admin
from .models import Attempt


class AttemptAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'problem',
        'part',
        'accepted',
    )
    list_filter = (
        'user',
        'part__problem',
        'part',
        'accepted',
    )
    search_fields = (
        'part__pk',
        'problem__title',
        'user__username',
        'part__description',
    )

    def problem(self, obj):
        return obj.part.problem
    problem.admin_order_field = 'part__problem'


admin.site.register(Attempt, AttemptAdmin)
