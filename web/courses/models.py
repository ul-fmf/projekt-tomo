from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from users.models import User
from utils.models import OrderWithRespectToMixin
from taggit.managers import TaggableManager


class Course(models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    students = models.ManyToManyField(User, blank=True, related_name='courses')
    teachers = models.ManyToManyField(User, blank=True, related_name='taught_courses')
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title

    def recent_problem_sets(self, n=3):
        return self.problem_sets.reverse().filter(visible=True)[:n]

    # show users courses
    def user_courses(self, user):
        return user.courses

    def is_teacher(self, user):
        return (user in self.teachers.all())

    def is_student(self, user):
        return (user in self.students.all())

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('course_detail', args=[str(self.pk)])

    def user_attempts(self, user):
        attempts = {}
        for attempt in user.attempts.filter(part__problem__problem_set__course=self):
            attempts[attempt.part_id] = attempt
        sorted_attempts = []
        for problem_set in self.problem_sets.all().prefetch_related('problems__parts'):
            problem_set_attempts = []
            for problem in problem_set.problems.all():
                problem_attempts = [attempts.get(part.pk) for part in problem.parts.all()]
                problem_set_attempts.append((problem, problem_attempts))
            sorted_attempts.append((problem_set, problem_set_attempts))
        return sorted_attempts

class ProblemSet(OrderWithRespectToMixin, models.Model):
    SOLUTION_HIDDEN = 'H'
    SOLUTION_VISIBLE_WHEN_SOLVED = 'S'
    SOLUTION_VISIBLE = 'V'
    SOLUTION_VISIBILITY_CHOICES = (
        (SOLUTION_HIDDEN, _('Hidden')),
        (SOLUTION_VISIBLE_WHEN_SOLVED, _('Visible when solved')),
        (SOLUTION_VISIBLE, _('Visible')),
    )
    course = models.ForeignKey(Course, related_name='problem_sets')
    title = models.CharField(max_length=70, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    visible = models.BooleanField(default=False, verbose_name=_('Visible'))
    solution_visibility = models.CharField(max_length=20,
                                           verbose_name=_('Solution visibility'),
                                           choices=SOLUTION_VISIBILITY_CHOICES,
                                           default=SOLUTION_VISIBLE_WHEN_SOLVED)
    tags = TaggableManager(blank=True)

    class Meta:
        order_with_respect_to = 'course'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('courses.views.problem_set_detail', args=[str(self.pk)])

    def attempts_archive(self, user):
        files = [problem.attempt_file(user) for problem in self.problems.all()]
        archive_name = slugify(self.title)
        return archive_name, files

    def edit_archive(self, user):
        files = [problem.edit_file(user) for problem in self.problems.all()]
        archive_name = "{0}-edit".format(slugify(self.title))
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

    def toggle_visible(self):
        self.visible = not self.visible
        self.save()

    def toggle_solution_visibility(self):
        next = {self.SOLUTION_HIDDEN: self.SOLUTION_VISIBLE_WHEN_SOLVED,
                self.SOLUTION_VISIBLE_WHEN_SOLVED: self.SOLUTION_VISIBLE,
                self.SOLUTION_VISIBLE: self.SOLUTION_HIDDEN}
        self.solution_visibility = next[self.solution_visibility]
        self.save()
