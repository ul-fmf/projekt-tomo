from django.db import models
from problems.models import Part
from users.models import User


class Attempt(models.Model):
    user = models.ForeignKey(User, related_name='attempts')
    part = models.ForeignKey(Part, related_name='attempts')
    solution = models.TextField(blank=True)
    accepted = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'part')
