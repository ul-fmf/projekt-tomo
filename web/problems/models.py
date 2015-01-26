from django.db import models


def shorten(s, max_length=50):
    if len(s) < max_length:
        return s
    else:
        return u'{0}...'.format(s[:50])


class Problem(models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.title


class Part(models.Model):
    problem = models.ForeignKey(Problem, related_name='parts')
    description = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    validation = models.TextField(blank=True)
    secret = models.TextField(default="[]")

    class Meta:
        order_with_respect_to = 'problem'

    def __unicode__(self):
        description = shorten(self.description)
        return u'{0}/#{1:06d} ({2})'.format(self.problem, self.id, description)
