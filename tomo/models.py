# -*- coding: utf-8 -*-
import json
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.query import QuerySet
from django.template.defaultfilters import slugify

class QuerySetManager(models.Manager):
    """A re-usable Manager to access a custom QuerySet"""
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)

    def get_query_set(self):
        return self.model.QuerySet(self.model)

class Language(models.Model):
    name = models.CharField(max_length=70)
    student_file = models.CharField(max_length=70)
    teacher_file = models.CharField(max_length=70)
    extension = models.CharField(max_length=4)

    def __unicode__(self):
        return u'{0}'.format(self.name)

    class Meta:
        ordering = ['name']

class Course(models.Model):
    name = models.CharField(max_length=70)
    shortname = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    students = models.ManyToManyField(User, related_name='courses', blank=True)
    teachers = models.ManyToManyField(User, related_name='taught_courses', blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    
    @classmethod
    def user_courses(self, user):
        return user.courses if user.is_authenticated() else self.objects

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
    timestamp = models.DateTimeField(auto_now=True)

    @models.permalink
    def get_absolute_url(self):
        return ('problem_set', [str(self.id)])

    def save(self, *args, **kwargs):
        self.course.save()
        super(ProblemSet, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{0}'.format(self.title)

    def default_language(self):
        try:
            return Language.objects.filter(problems__problem_set=self).latest('problems__timestamp')
        except Problem.DoesNotExist:
            return

    class QuerySet(QuerySet):
        def success(self, user):
            if user.is_authenticated():
                correct = dict(
                    Attempt.objects.filter(
                        active=True, correct=True, part__problem__problem_set__in=self,
                        submission__user=user
                    ).values(
                        'part__problem__problem_set'
                    ).order_by(
                        'part__problem__problem_set'
                    ).annotate(
                        correct_count=models.Count('part__problem__problem_set')
                    ).values_list('part__problem__problem_set', 'correct_count')
                )
                total = dict(
                    self.annotate(
                        part_count=models.Count('problems__parts')
                    ).values_list('id', 'part_count')
                )
                success = dict((problem_set_id, int(100 * correct.get(problem_set_id, 0) / tot if tot else 0)) for
                            problem_set_id, tot in total.items())
                return success
            else:
                return {}


    class Meta:
        order_with_respect_to = 'course'

class Problem(models.Model):
    author = models.ForeignKey(User, related_name='problems')
    language = models.ForeignKey(Language, related_name='problems')
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    preamble = models.TextField(blank=True)
    problem_set = models.ForeignKey(ProblemSet, related_name='problems')

    def __unicode__(self):
        return u'{0}'.format(self.title)

    def save(self, *args, **kwargs):
        self.problem_set.save()
        super(Problem, self).save(*args, **kwargs)

    def filename(self):
        return u'{0}.{1}'.format(slugify(self.title), self.language.extension)

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
    timestamp = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'#{0} ({1})'.format(self._order + 1, self.id)

    def save(self, *args, **kwargs):
        self.problem.save()
        super(Part, self).save(*args, **kwargs)

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

        def for_problem(self, problem):
            return self.filter(part__problem=problem)

        def for_problem_set(self, problem_set):
            return self.filter(part__problem__problem_set=problem_set)

        def user_attempts(self, user):
            if user.is_authenticated():
                attempts = self.filter(active=True, submission__user=user)
                return dict((attempt.part_id, attempt) for attempt in attempts)
            else:
                return {}
    
    def error_list(self):
        return json.loads(self.errors)

    class Meta:
        ordering = ['submission']
