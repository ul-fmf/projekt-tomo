import json
from django.db import models
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from rest_framework.authtoken.models import Token
from simple_history.models import HistoricalRecords
from utils import is_json_string_list, truncate
from courses.models import ProblemSet


class Problem(models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    problem_set = models.ForeignKey(ProblemSet, related_name='problems', null=True)
    history = HistoricalRecords()

    def __unicode__(self):
        return self.title

    def user_attempts(self, user):
        return user.attempts.filter(part__problem=self)

    def user_solutions(self, user):
        return {attempt.part.id: attempt.solution for attempt in self.user_attempts(user)}

    def attempt_file(self, url, user=None):
        authentication_token = Token.objects.get(user=user) if user else None
        solutions = self.user_solutions(user) if user else {}
        parts = [(part, solutions.get(part.id, '')) for part in self.parts.all()]
        filename = "{0}.py".format(slugify(self.title))
        contents = render_to_string("python/attempt.py", {
            "problem": self,
            "parts": parts,
            "submission_url": url,
            "authentication_token": authentication_token
        })
        return filename, contents


class Part(models.Model):
    problem = models.ForeignKey(Problem, related_name='parts')
    description = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    validation = models.TextField(blank=True)
    secret = models.TextField(default="[]", validators=[is_json_string_list])
    history = HistoricalRecords()

    class Meta:
        order_with_respect_to = 'problem'

    def __unicode__(self):
        return u'@{0:06d} ({1})'.format(self.pk, truncate(self.description))

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
