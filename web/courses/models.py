from django.db import models
from django.template.defaultfilters import slugify
from users.models import User


class Course(models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    students = models.ManyToManyField(User, blank=True, related_name='courses')
    teachers = models.ManyToManyField(User, blank=True, related_name='taught_courses')

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title

    def recent_problem_sets(self):
        return self.problem_sets.reverse()[:3]


class ProblemSet(models.Model):
    HIDDEN = 'H'
    VISIBLE_WHEN_SOLVED = 'S'
    VISIBLE = 'V'
    SOLUTION_VISIBILITY_CHOICES = (
        (HIDDEN, 'Hidden'),
        (VISIBLE_WHEN_SOLVED, 'Visible when solved'),
        (VISIBLE, 'Visible'),
    )
    course = models.ForeignKey(Course, related_name='problem_sets')
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    visible = models.BooleanField(default=False)
    solution_visibility = models.CharField(max_length=20, default=VISIBLE_WHEN_SOLVED,
                                           choices=SOLUTION_VISIBILITY_CHOICES)

    class Meta:
        order_with_respect_to = 'course'

    def __unicode__(self):
        return self.title

    def attempts_archive(self, url, user):
        files = [problem.attempt_file(url, user=user) for problem in self.problems.all()]
        archive_name = slugify(self.title)
        return archive_name, files
