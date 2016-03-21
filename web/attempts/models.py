from django.db import models
from simple_history.models import HistoricalRecords
from users.models import User
from utils import is_json_string_list


class Attempt(models.Model):
    user = models.ForeignKey(User, related_name='attempts')
    part = models.ForeignKey('problems.Part', related_name='attempts')
    solution = models.TextField(blank=True)
    valid = models.BooleanField(default=False)
    feedback = models.TextField(default='[]', validators=[is_json_string_list])
    history = HistoricalRecords()

    class Meta:
        unique_together = ('user', 'part')

    def __unicode__(self):
        return u'{} vs. @{:06d}: {}'.format(self.user.username, self.part.pk,
                                            'valid' if self.valid else 'invalid')
