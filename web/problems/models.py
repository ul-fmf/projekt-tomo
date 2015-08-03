import json
from django.db import models
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from rest_framework.authtoken.models import Token
from simple_history.models import HistoricalRecords
from utils import is_json_string_list, truncate
from courses.models import ProblemSet
from utils.models import OrderWithRespectToMixin
from taggit.managers import TaggableManager


class Problem(OrderWithRespectToMixin, models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    problem_set = models.ForeignKey(ProblemSet, related_name='problems')
    history = HistoricalRecords()
    tags = TaggableManager(blank=True)

    class Meta:
        order_with_respect_to = 'problem_set'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '{}#{}'.format(self.problem_set.get_absolute_url(), self.anchor())

    def anchor(self):
        return 'problem-{}'.format(self.pk)

    def user_attempts(self, user):
        return user.attempts.filter(part__problem=self)

    def user_solutions(self, user):
        return {attempt.part.id: attempt.solution for attempt in self.user_attempts(user)}

    def attempt_file(self, url, user):
        authentication_token = Token.objects.get(user=user)
        solutions = self.user_solutions(user)
        parts = [(part, solutions.get(part.id, '')) for part in self.parts.all()]
        filename = "{0}.py".format(slugify(self.title))
        contents = render_to_string("python/attempt.py", {
            "problem": self,
            "parts": parts,
            "submission_url": url,
            "authentication_token": authentication_token
        })
        return filename, contents

    def edit_file(self, url, user):
        authentication_token = Token.objects.get(user=user)
        filename = "{0}-edit.py".format(slugify(self.title))
        contents = render_to_string("python/edit.py", {
            "problem": self,
            "submission_url": url,
            "authentication_token": authentication_token
        })
        return filename, contents

    def valid(self, user):
        '''
        Check whether user has valid attempts for all parts of
        this problem.
        '''
        return self.valid_parts(user).count() == self.parts.count()

    def invalid(self, user):
        '''
        Check whether user has some invalid attempts for this problem.
        '''
        return self.attempted(user) and self.valid_parts(user).count() == 0

    def valid_parts(self, user):
        '''
        Return the QuerySet object of problem parts that have valid attempt by the given
        user.
        '''
        return self.parts.filter(attempts__user=user, attempts__valid=True)

    def attempted_parts(self, user):
        '''
        Return the queryset of all parts for which user has submitted attempts for.
        '''
        return user.attempts.filter(part__in=self.parts.all())

    def attempted(self, user):
        '''
        Return the queryset of all parts for which user has submitted attempts for.
        '''
        return self.attempted_parts(user).count() > 0


class Part(OrderWithRespectToMixin, models.Model):
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

    def get_absolute_url(self):
        return self.problem.get_absolute_url()

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

    def valid(self, user):
        '''
        Check whether user has submitted attempt for this part
        that is marked as valid.
        '''
        return user.attempts.filter(part=self, valid=True).count() == 1

    def attempted(self, user):
        '''
        Check whether user has submitted attempt for this part.
        '''
        return user.attempts.filter(part=self).count() >= 1
