from django.db import models
from django.template.defaultfilters import slugify
from users.models import User
from utils.models import OrderWithRespectToMixin


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


class ProblemSet(OrderWithRespectToMixin, models.Model):
    SOLUTION_HIDDEN = 'H'
    SOLUTION_VISIBLE_WHEN_SOLVED = 'S'
    SOLUTION_VISIBLE = 'V'
    SOLUTION_VISIBILITY_CHOICES = (
        (SOLUTION_HIDDEN, 'Hidden'),
        (SOLUTION_VISIBLE_WHEN_SOLVED, 'Visible when solved'),
        (SOLUTION_VISIBLE, 'Visible'),
    )
    course = models.ForeignKey(Course, related_name='problem_sets')
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    visible = models.BooleanField(default=False)
    solution_visibility = models.CharField(max_length=20,
                                           choices=SOLUTION_VISIBILITY_CHOICES,
                                           default=SOLUTION_VISIBLE_WHEN_SOLVED)

    class Meta:
        order_with_respect_to = 'course'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('courses.views.problem_set_detail', args=[str(self.pk)])

    def attempts_archive(self, url, user):
        files = [problem.attempt_file(url, user=user) for problem in self.problems.all()]
        archive_name = slugify(self.title)
        return archive_name, files

    def valid_percentage(self, user):
        '''
        Returns an integer value representing the percentage (rounded to the nearest integer)
        of parts in this problemset for which  the given user has a valid attempt.
        '''
        number_of_all_parts = sum([problem.parts.count() for problem in self.problems.all()])
        number_of_valid_parts = sum([problem.valid_parts(user).count()
                                     for problem in self.problems.all()])
        if number_of_all_parts == 0:
            return None
        else:
            return int(round(100.0 * number_of_valid_parts / number_of_all_parts))

    def attempted_problems(self, user):
        return self.problems.filter(parts__attempts__user=user)

    def invalid_problems(self, user):
        return [problem for problem in self.attempted_problems(user) if problem.invalid(user)]

    def valid_problems(self, user):
        return [problem for problem in self.attempted_problems(user) if problem.valid(user)]
