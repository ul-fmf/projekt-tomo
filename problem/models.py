# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=70, unique=True)
    description = models.TextField(blank=True)
    students = models.ManyToManyField(User, related_name='courses')

    def __unicode__(self):
        return u'{0}'.format(self.name)
    
    class Meta:
        ordering = ['name']


class Collection(models.Model):
    STATUS = (
        ('10', 'v pripravi'),
        ('20', 'izpit'),
        ('30', 'vaje'),
        ('40', 'rešitve')
    )
    name = models.CharField(max_length=70, unique=True)
    description = models.TextField(blank=True)
    problems = models.ManyToManyField('Problem', related_name='collections')
    status = models.CharField(max_length=2, choices=STATUS, default='10')

    def __unicode__(self):
        return u'{0}'.format(self.name)

    class Meta:
        ordering = ['id']


class Problem(models.Model):
    name = models.CharField(max_length=70, unique=True)
    description = models.TextField(blank=True)
    preamble = models.TextField(blank=True)

    def __unicode__(self):
        return u'{0}'.format(self.name)

    class Meta:
        ordering = ['name']


class Part(models.Model):
    problem = models.ForeignKey(Problem, related_name='parts')
    description = models.TextField(blank=True)
    trial = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    answers = models.TextField(blank=True)

    def __unicode__(self):
        return u'{0} ({1})'.format(self.problem.name, self._order + 1)

    class Meta:
        order_with_respect_to = 'problem'


class Submission(models.Model):
    user = models.ForeignKey(User, related_name='submissions')
    collection = models.ForeignKey(Collection, related_name='submissions')
    conflicting = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.TextField()
    download_ip = models.IPAddressField(editable=False)
    upload_ip = models.IPAddressField(editable=False)

    def __unicode__(self):
        user = self.user.get_full_name() or self.user.username
        return u'{0}, {1:%H:%M, %d.%m.%y}'.format(user, self.timestamp)

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']



# SELECT t1.user_id, t1.id
# FROM problem_submission AS t1
#   LEFT OUTER JOIN problem_submission AS t2
#     ON (t1.user_id = t2.user_id AND t1.id < t2.id)
# WHERE t2.id IS NULL;

# select f.user_id, f.id
# from (
#    select user_id, max(timestamp) as maxid
#    from problem_submission group by user_id
# ) as x inner join problem_submission as f on f.user_id = x.user_id and f.timestamp = x.maxid;

class Solution(models.Model):
    part = models.ForeignKey(Part, related_name='solutions')
    submission = models.ForeignKey(Submission, related_name='solutions')
    start = models.IntegerField()
    end = models.IntegerField()
    correct = models.BooleanField()

    def __unicode__(self):
        return u'{0}, {1}'.format(self.part, self.submission)
    
    class Meta:
        order_with_respect_to = 'submission'
