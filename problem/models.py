# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.query import QuerySet

class QuerySetManager(models.Manager):
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.model.QuerySet(self.model), attr, *args)

class Course(models.Model):
    name = models.CharField(max_length=70)
    shortname = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    students = models.ManyToManyField(User, related_name='courses', blank=True)
    teachers = models.ManyToManyField(User, related_name='taught_courses', blank=True)

    def recent(self):
        return self.problem_sets.reverse()[:3]

    @models.permalink
    def get_absolute_url(self):
        return ('course', [str(self.id)])

    def __unicode__(self):
        return u'{0} ({1})'.format(self.name, self.shortname)

    class Meta:
        ordering = ['name']


class ProblemSet(models.Model):
    SOLUTION_VISIBILITY = (
        ('skrite', 'skrite'),
        ('pogojno', 'vidne, ko je naloga rešena'),
        ('vidne', 'vidne'),
    )
    course = models.ForeignKey(Course, related_name='problem_sets')
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    visible = models.BooleanField()
    solution_visibility = models.CharField(max_length=20, default='pogojno',
                                           choices=SOLUTION_VISIBILITY)
    objects = QuerySetManager()

    def solved(self, user):
        all_parts = Part.objects.filter(problem__problem_set=self).count()
        if all_parts > 0 and user.is_authenticated():
            solved_parts = Attempt.objects.from_user(user).filter(
                                                  part__problem__problem_set=self,
                                                  correct=True).count()
            return int(100 * solved_parts / all_parts)
        else:
            return 0

    @models.permalink
    def get_absolute_url(self):
        return ('problem_set', [str(self.id)])

    def __unicode__(self):
        return u'{0}'.format(self.title)

    class QuerySet(QuerySet):
        def get_for_user(self, problem_set_id, user):
            problem_set = ProblemSet.objects.get(id=problem_set_id)
            if problem_set.visible or user.is_staff:
                return problem_set
            else:
                raise PermissionDenied

    class Meta:
        order_with_respect_to = 'course'

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
    problem_set = models.ForeignKey(ProblemSet, related_name='problems')
    objects = QuerySetManager()

    def __unicode__(self):
        return u'{0}'.format(self.title)

    def solved(self, user):
        all_parts = self.parts.count()
        if all_parts > 0 and user.is_authenticated():
            solved_parts = Attempt.objects.from_user(user).filter(part__problem=self,
                                                  correct=True).count()
            return int(100 * solved_parts / all_parts)
        else:
            return 0

    def visible(self, user):
        return self.problem_set.visible or user.is_staff

    def get_absolute_url(self):
        return "{0}#problem-{1}".format(self.problem_set.get_absolute_url(), self.id)

    class QuerySet(QuerySet):
        def get_for_user(self, problem_id, user):
            problem = Problem.objects.get(id=problem_id)
            if problem.problem_set.visible or user.is_staff:
                return problem
            else:
                raise PermissionDenied

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
    objects = QuerySetManager()

    class QuerySet(QuerySet):
        def active(self):
            return self.filter(active=True)

        def from_user(self, user):
            if user.is_authenticated:
                return self.filter(active=True, submission__user=user)
            else:
                return self.none()

        def for_problem(self, problem):
            return self.filter(part__problem=problem)

        def for_problem_set(self, problem_set):
            return self.filter(part__problem__problem_set=problem_set)

        def dict_by_part(self):
            return dict((attempt.part_id, attempt) for attempt in self)

    class Meta:
        ordering = ['submission']
