from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from users.models import User
from utils.models import OrderWithRespectToMixin
from taggit.managers import TaggableManager
from attempts.models import Attempt
from problems.models import Part


class Course(models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    students = models.ManyToManyField(User, blank=True, related_name='courses')
    teachers = models.ManyToManyField(User, blank=True, related_name='taught_courses')
    institution = models.CharField(max_length=140)
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return u'{} @{{{}}}'.format(self.title, self.institution)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('course_detail', args=[str(self.pk)])

    def recent_problem_sets(self, n=3):
        return self.problem_sets.reverse().filter(visible=True)[:n]

    def user_attempts(self, user):
        attempts = {}
        for attempt in user.attempts.filter(part__problem__problem_set__course=self):
            attempts[attempt.part_id] = attempt
        sorted_attempts = []
        for problem_set in self.problem_sets.all().prefetch_related('problems__parts'):
            problem_set_attempts = []
            prob_set_valid = prob_set_invalid = prob_set_empty = 0
            for problem in problem_set.problems.all():
                valid = invalid = empty = 0
                problem_attempts = [attempts.get(part.pk) for part in problem.parts.all()]
                for attempt in problem_attempts:
                    if attempt is None:
                        empty += 1
                    elif attempt.valid:
                        valid += 1
                    else:
                        invalid += 1
                problem_set_attempts.append((problem, problem_attempts, valid, invalid, empty))
                prob_set_valid += valid
                prob_set_invalid += invalid
                prob_set_empty += empty
            sorted_attempts.append((problem_set, problem_set_attempts, prob_set_valid, prob_set_invalid, prob_set_empty))
        return sorted_attempts

    def annotate_for_user(self, user):
        self.is_taught = user.can_edit_course(self)
        self.is_favourite = user.is_favourite_course(self)
        self.annotated_problem_sets = []
        for problem_set in self.problem_sets.all():
            if user.can_view_problem_set(problem_set):
                problem_set.percentage = problem_set.valid_percentage(user)
                if problem_set.percentage is None:
                    problem_set.percentage = 0
                problem_set.grade = min(5, int(problem_set.percentage / 20) + 1)
                self.annotated_problem_sets.append(problem_set)


class ProblemSet(OrderWithRespectToMixin, models.Model):
    SOLUTION_HIDDEN = 'H'
    SOLUTION_VISIBLE_WHEN_SOLVED = 'S'
    SOLUTION_VISIBLE = 'V'
    SOLUTION_VISIBILITY_CHOICES = (
        (SOLUTION_HIDDEN, _('Official solutions are hidden')),
        (SOLUTION_VISIBLE_WHEN_SOLVED, _('Official solutions are visible when solved')),
        (SOLUTION_VISIBLE, _('Official solutions are visible')),
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

    def student_success(self):
        student_count = self.course.students.count()
        attempts = Attempt.objects.filter(user__courses=self.course,
                                          part__problem__problem_set=self)
        submitted_count = attempts.count()
        valid_count = attempts.filter(valid=True).count()
        part_count = Part.objects.filter(problem__problem_set=self).count()
        invalid_count = submitted_count - valid_count
        total_count = student_count * part_count

        if total_count:
            valid_percentage = int(100.0 * valid_count / total_count)
            invalid_percentage = int(100.0 * invalid_count / total_count)
        else:
            valid_percentage = 0
            invalid_percentage = 0

        empty_percentage = 100 - valid_percentage - invalid_percentage
        return {
            'valid': valid_percentage,
            'invalid': invalid_percentage,
            'empty': empty_percentage,
            'grade': min(5, int(valid_percentage / 20) + 1)
        }

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
