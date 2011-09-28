# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models


class Problem(models.Model):
    author = models.ForeignKey(User, related_name='problems')
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    preamble = models.TextField(blank=True)
    revealed = models.BooleanField()

    def __unicode__(self):
        return u'{0}'.format(self.title)

    class Meta:
        ordering = ['title']


class Part(models.Model):
    problem = models.ForeignKey(Problem, related_name='parts')
    description = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    validation = models.TextField(blank=True)
    challenge = models.TextField(default='')

    def __unicode__(self):
        return u'#{0}'.format(self._order + 1)

    class Meta:
        order_with_respect_to = 'problem'


class Submission(models.Model):
    user = models.ForeignKey(User, related_name='submissions')
    problem = models.ForeignKey(Problem, related_name='submissions')
    timestamp = models.DateTimeField(auto_now_add=True)
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
