# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

from tomo.problem.models import Part, Attempt

class Course(models.Model):
    name = models.CharField(max_length=70)
    shortname = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    students = models.ManyToManyField(User, related_name='courses', blank=True)
    teachers = models.ManyToManyField(User, related_name='taught_courses', blank=True)

    def recent(self):
        return self.problem_sets.all()[:3]

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

    def solved(self, user):
        all_parts = Part.objects.filter(problem__problem_set=self).count()
        if all_parts > 0 and user.is_authenticated():
            solved_parts = Attempt.objects.filter(submission__user=user,
                                                  part__problem__problem_set=self,
                                                  active=True,
                                                  correct=True).count()
            return int(100 * solved_parts / all_parts)
        else:
            return 0


    def __unicode__(self):
        return u'{0}'.format(self.title)

    class Meta:
        order_with_respect_to = 'course'
