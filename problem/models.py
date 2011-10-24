from django.contrib.auth.models import User
from django.db import models


class Language(models.Model):
    name = models.CharField(max_length=70)
    download_file = models.CharField(max_length=70)
    edit_file = models.CharField(max_length=70)
    extension = models.CharField(max_length=4)

    def __unicode__(self):
        return u'{0}'.format(self.name)

    class Meta:
        ordering = ['name']

class Problem(models.Model):
    author = models.ForeignKey(User, related_name='problems')
    language = models.ForeignKey(Language, related_name='problems')
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    preamble = models.TextField(blank=True)
    problem_set = models.ForeignKey('course.ProblemSet', related_name='problems')

    def __unicode__(self):
        return u'{0}'.format(self.title)

    def solved(self, user):
        all_parts = self.parts.count()
        if all_parts > 0 and user.is_authenticated():
            solved_parts = Attempt.objects.filter(submission__user=user,
                                                  part__problem=self, active=True,
                                                  correct=True).count()
            return int(100 * solved_parts / all_parts)
        else:
            return 0

    def get_absolute_url(self):
        return "{0}#problem-{1}".format(self.problem_set.get_absolute_url(), self.id)

    class Meta:
        order_with_respect_to = 'problem_set'


class Part(models.Model):
    problem = models.ForeignKey(Problem, related_name='parts')
    description = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    validation = models.TextField(blank=True)
    challenge = models.TextField(blank=True)

    def __unicode__(self):
        return u'#{0} ({1})'.format(self._order + 1, self.id)

    class Meta:
        order_with_respect_to = 'problem'


class Submission(models.Model):
    user = models.ForeignKey(User, related_name='submissions')
    problem = models.ForeignKey(Problem, related_name='submissions')
    timestamp = models.DateTimeField(auto_now_add=True)
    preamble = models.TextField(blank=True)
    source = models.TextField(blank=True)

    class Meta:
        ordering = ['-id']


class Attempt(models.Model):
    part = models.ForeignKey(Part, related_name='attempts')
    submission = models.ForeignKey(Submission, related_name='attempts')
    solution = models.TextField(blank=True)
    errors = models.TextField(default="{}")
    correct = models.BooleanField()
    active = models.BooleanField()

    class Meta:
        ordering = ['submission']
