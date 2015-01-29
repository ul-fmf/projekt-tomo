from django.db import models
from problems.models import Part
from users.models import User
from utils import is_json_string_list


class Attempt(models.Model):
    user = models.ForeignKey(User, related_name='attempts')
    part = models.ForeignKey(Part, related_name='attempts')
    solution = models.TextField(blank=True)
    valid = models.BooleanField(default=False)
    feedback = models.TextField(default="[]", validators=[is_json_string_list])

    class Meta:
        unique_together = ('user', 'part')
