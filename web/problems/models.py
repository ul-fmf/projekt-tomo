import json
from django.db import models
from utils import is_json_string_list, shorten


class Problem(models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.title


class Part(models.Model):
    problem = models.ForeignKey(Problem, related_name='parts')
    description = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    validation = models.TextField(blank=True)
    secret = models.TextField(default="[]", validators=[is_json_string_list])

    class Meta:
        order_with_respect_to = 'problem'

    def __unicode__(self):
        return u'#{0:06d} ({1})'.format(self.pk, shorten(self.description))

    def check_secret(self, secret):
        '''
        Checks whether a submitted secret corresponds to the official one.

        The function accepts a secret (list of strings) and returns the pair:
        True, None -- if secret matches the official one
        False, None -- if secret has an incorrect length
        False, i -- if secret first differs from the official one at index i
        '''
        official_secret = json.loads(self.secret)
        if len(official_secret) != len(secret):
            return False, None
        for i in range(len(secret)):
            if secret[i] != official_secret[i]:
                return False, i
        return True, None
