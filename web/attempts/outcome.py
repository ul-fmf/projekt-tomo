from dataclasses import dataclass

from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from .models import Attempt


def _group_sizes(queryset, *group_by):
    if group_by:
        return {
            tuple(group): count
            for *group, count in queryset.values_list(*group_by).annotate(Count("id"))
        }
    else:
        return {(): queryset.count()}


@dataclass
class Outcome:
    valid: int = 0
    invalid: int = 0
    total: int = 0

    def __add__(self, other):
        return Outcome(
            self.valid + other.valid,
            self.invalid + other.invalid,
            self.total + other.total,
        )

    @property
    def empty(self):
        return self.total - self.valid - self.invalid

    @property
    def valid_percentage(self):
        return int(100 * self.valid / self.total) if self.total else 0

    @property
    def invalid_percentage(self):
        return int(100 * self.invalid / self.total) if self.total else 0

    @property
    def empty_percentage(self):
        return 100 - self.valid_percentage - self.invalid_percentage

    @property
    def grade(self):
        return min(5, int(5 * self.valid / self.total) + 1) if self.total else 0

    def summary(self):
        valid = f'{self.valid} { _("valid") }'
        invalid = f'{self.invalid} { _("invalid") }'
        empty = f'{self.empty} { _("empty") }'
        return f"{valid} / {invalid} / {empty}"

    def percentage_summary(self):
        valid = f'{self.valid_percentage}% { _("valid") }'
        invalid = f'{self.invalid_percentage}% { _("invalid") }'
        empty = f'{self.empty_percentage}% { _("empty") }'
        return f"{valid} / {invalid} / {empty}"

    @classmethod
    def group_dict(cls, parts, users, parts_group_by, users_group_by):
        part_group_sizes = _group_sizes(parts, *parts_group_by)
        user_group_sizes = _group_sizes(users, *users_group_by)
        outcomes = {}
        for part_group, part_group_size in part_group_sizes.items():
            for user_group, user_group_size in user_group_sizes.items():
                outcomes[part_group + user_group] = cls(
                    total=part_group_size * user_group_size
                )
        attempts = Attempt.objects.filter(part__in=parts, user__in=users).distinct()
        group_by = [f"part__{g}" for g in parts_group_by] + [
            f"user__{g}" for g in users_group_by
        ]
        for (*group, valid), count in _group_sizes(
            attempts, *group_by, "valid"
        ).items():
            outcomes[tuple(group)] += cls(valid=count) if valid else cls(invalid=count)
        return outcomes
