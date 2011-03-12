from django.contrib.auth.models import User
from django.db import models


class Problem(models.Model):
    name = models.CharField(max_length=70, unique=True)
    description = models.TextField(blank=True)
    trial = models.TextField(blank=True)

    def __unicode__(self):
        return u'{0}'.format(self.name)

    @models.permalink
    def get_absolute_url(self):
        return ('show_problem', [self.id])


class Part(models.Model):
    problem = models.ForeignKey(Problem, related_name='parts')
    description = models.TextField(blank=True)
    trial = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    secret = models.CharField(max_length=32)

    def __unicode__(self):
        return u'{0} ({1})'.format(self.problem.name, self.id)

    class Meta:
        order_with_respect_to = 'problem'


class Submission(models.Model):
    user = models.ForeignKey(User, related_name='submissions')
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


class Solution(models.Model):
    user = models.ForeignKey(User, related_name='solutions')
    part = models.ForeignKey(Part, related_name='solutions')
    submission = models.ForeignKey(Submission, related_name='solutions')
    start = models.IntegerField(editable=False)
    end = models.IntegerField(editable=False)
    label = models.CharField(max_length=32, blank=True)
    correct = models.BooleanField()

    def __unicode__(self):
        return u'{0} {1}) {2}'.format(self.part.problem.name, self.label,
                                      self.submission)
    
    def solution(self):
        return self.submission.source[self.start:self.end].strip()
    
    class Meta:
        order_with_respect_to = 'submission'
