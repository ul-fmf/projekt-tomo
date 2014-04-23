# -*- coding: utf-8 -*-
import json
from django.contrib.auth.models import User
from django.db import models
from django.db.models.query import QuerySet
from problems.models import Problem, Part


class QuerySetManager(models.Manager):
    """A re-usable Manager to access a custom QuerySet"""
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)

    def get_query_set(self):
        return self.model.QuerySet(self.model)


class Submission(models.Model):
    user = models.ForeignKey(User, related_name='submissions')
    problem = models.ForeignKey(Problem, related_name='submissions')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip = models.IPAddressField()
    preamble = models.TextField(blank=True)

    class Meta:
        ordering = ['-id']


class Attempt(models.Model):
    part = models.ForeignKey(Part, related_name='attempts')
    submission = models.ForeignKey(Submission, related_name='attempts')
    solution = models.TextField(blank=True)
    errors = models.TextField(default="{}")
    correct = models.BooleanField()
    active = models.BooleanField()
    objects = QuerySetManager()

    class Meta:
        ordering = ['submission']

    class QuerySet(QuerySet):
        def active(self):
            return self.filter(active=True)

        def for_problem(self, problem):
            return self.filter(part_id__in=problem.parts.all())

        def for_problem_set(self, problem_set):
            part_ids = Part.objects.filter(problem__problem_set=problem_set)
            return self.filter(part_id__in=part_ids)

        def user_attempts(self, user):
            if user.is_authenticated():
                attempts = self.filter(active=True, submission__user=user)
                return dict((attempt.part_id, attempt) for attempt in attempts)
            else:
                return {}

    def error_list(self):
        return json.loads(self.errors)
