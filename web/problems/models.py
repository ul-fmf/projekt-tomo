import json
from django.core.exceptions import ValidationError
from django.db import models


def shorten(s, max_length=50):
    if len(s) < max_length:
        return s
    else:
        return u'{0}...'.format(s[:50])


def is_json_string_list(s):
    try:
        val = json.loads(s)
    except ValueError:
        raise ValidationError('Not a JSON value.')
    if type(val) is not list:
        raise ValidationError('Not a JSON list.')
    for x in val:
        if type(x) is not unicode:
            raise ValidationError('Not a JSON list of strings.')


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
        description = shorten(self.description)
        return u'{0}/#{1:06d} ({2})'.format(self.problem, self.id, description)

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
        for s1, (s2, i) in zip(official_secret, enumerate(secret)):
            if s1 != s2:
                return False, i
        return True, None
