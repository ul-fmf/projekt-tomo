from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Attempt


class AttemptAdmin(SimpleHistoryAdmin):
    list_display = (
        'user',
        'problem',
        'part',
        'valid',
    )
    list_filter = (
        'user',
        'part__problem',
        'part',
        'valid',
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
