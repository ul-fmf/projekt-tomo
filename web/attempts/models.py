from django.db import models
from simple_history.models import HistoricalRecords
from problems.models import Part
from users.models import User
from utils import is_json_string_list


class Attempt(models.Model):
    user = models.ForeignKey(User, related_name='attempts')
    part = models.ForeignKey(Part, related_name='attempts')
    solution = models.TextField(blank=True)
    valid = models.BooleanField(default=False)
    feedback = models.TextField(default="[]", validators=[is_json_string_list])
    history = HistoricalRecords()

    def changed_fields(self, validated_data):
        return [attribute
                for (attribute, value) in validated_data.items()
                if value != getattr(self, attribute)
                ]

    def update_fields(self, dictionary):
        changed_fields = self.changed_fields(dictionary)
        map(lambda attribute: setattr(self, attribute, dictionary[attribute]),
            changed_fields)
        return changed_fields

    class Meta:
        unique_together = ('user', 'part')
