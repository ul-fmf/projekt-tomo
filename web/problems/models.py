import json
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from rest_framework.authtoken.models import Token
from simple_history.models import HistoricalRecords
from utils import is_json_string_list, truncate
from utils.models import OrderWithRespectToMixin
from taggit.managers import TaggableManager


class ProblemContents(OrderWithRespectToMixin, models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    problem_set = models.ForeignKey('courses.ProblemSet', related_name='problems')
    history = HistoricalRecords()
    tags = TaggableManager(blank=True)
    language = models.CharField(max_length=8, choices=(
        ('python', 'Python 3'),
        ('octave', 'Octave')), default='python')
    EXTENSIONS = {'python': 'py', 'octave': 'm'}
    class Meta:
        order_with_respect_to = 'problem_set'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '{}#{}'.format(self.problem_set.get_absolute_url(), self.anchor())

    def anchor(self):
        return 'problem-{}'.format(self.pk)

    def user_attempts(self, user):
        return user.attempts.filter(part__problem=self)

    def user_solutions(self, user):
        return {attempt.part.id: attempt.solution for attempt in self.user_attempts(user)}

    def attempt_file(self, user):
        authentication_token = Token.objects.get(user=user)
        solutions = self.user_solutions(user)
        parts = [(part, solutions.get(part.id, '')) for part in self.parts.all()]
        url = settings.SUBMISSION_URL + reverse('attempts-submit')
        problem_slug = slugify(self.title).replace("-", "_")
        extension = self.EXTENSIONS[self.language]
        filename = "{0}.{1}".format(problem_slug, extension)
        contents = render_to_string("{0}/attempt.{1}".format(self.language, extension), {
            "problem": self,
            "parts": parts,
            "submission_url": url,
            "authentication_token": authentication_token
        })
        return filename, contents

    def marking_file(self, user):
        attempts = {attempt.part.id: attempt for attempt in self.user_attempts(user)}
        parts = [(part, attempts.get(part.id)) for part in self.parts.all()]
        username = user.get_full_name() or user.username
        problem_slug = slugify(username).replace("-", "_")
        extension = self.EXTENSIONS[self.language]
        filename = "{0}.{1}".format(problem_slug, extension)
        contents = render_to_string("{0}/marking.{1}".format(self.language, extension), {
            "problem": self,
            "parts": parts,
            "user": user,
        })
        return filename, contents

    def edit_file(self, user):
        authentication_token = Token.objects.get(user=user)
        url = settings.SUBMISSION_URL + reverse('problems-submit')
        problem_slug = slugify(self.title).replace("-", "_")
        filename = "{0}_edit.{1}".format(problem_slug, self.EXTENSIONS[self.language])
        contents = render_to_string("{0}/edit.{1}".format(self.language, self.EXTENSIONS[self.language]), {
            "problem": self,
            "submission_url": url,
            "authentication_token": authentication_token
        })
        return filename, contents

    def attempts_by_user(self):
        attempts = {}
        for part in self.parts.all():
            for attempt in part.attempts.all():
                if attempt.user in attempts:
                    attempts[attempt.user][part] = attempt
                else:
                    attempts[attempt.user] = {part: attempt}
        for student in self.problem_set.course.students.all():
            if student not in attempts:
                attempts[student] = {}
        observed_students = list(self.problem_set.course.observed_students())
        print(observed_students)
        for user in observed_students:
            user.valid = user.invalid = user.empty = 0
            user.these_attempts = [attempts[user].get(part) for part in self.parts.all()]
            for attempt in user.these_attempts:
                if attempt is None:
                    user.empty += 1
                elif attempt.valid:
                    user.valid += 1
                else:
                    user.invalid += 1
        return observed_students

    def copy_to(self, problem_set):
        new_problem = ProblemContents()
        new_problem.title = self.title
        new_problem.description = self.description
        new_problem.problem_set = problem_set
        new_problem.tags = self.tags
        new_problem.save()
        for part in self.parts.all():
            part.copy_to(new_problem)
        return new_problem



class Part(OrderWithRespectToMixin, models.Model):
    problem = models.ForeignKey(ProblemContents, related_name='parts')
    description = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    validation = models.TextField(blank=True)
    secret = models.TextField(default="[]", validators=[is_json_string_list])
    history = HistoricalRecords()

    class Meta:
        order_with_respect_to = 'problem'

    def __str__(self):
        return '@{0:06d} ({1})'.format(self.pk, truncate(self.description))

    def get_absolute_url(self):
        return '{}#{}'.format(self.problem_set.get_absolute_url(), self.anchor())

    def anchor(self):
        return 'part-{}'.format(self.pk)


    def check_secret(self, secret):
        '''
        Checks whether a submitted secret corresponds to the official one.

        The function accepts a secret (list of strings) and returns the pair:
        True, None -- if secret matches the official one
        False, None -- if secret has an incorrect length
        False, i -- if secret first differs from the official one at index i
        '''
        official_secret = json.loads(self.secret)
        if len(official_secret) != len(secret):
            return False, None
        for i in range(len(secret)):
            if secret[i] != official_secret[i]:
                return False, i
        return True, None

    def student_success(self):
        students = self.problem.problem_set.course.observed_students()
        student_count = len(students)
        attempts = self.attempts.filter(user__in=students)
        submitted_count = attempts.count()
        valid_count = attempts.filter(valid=True).count()
        invalid_count = submitted_count - valid_count
        empty_count = student_count - valid_count - invalid_count

        return {
            'valid': valid_count,
            'invalid': invalid_count,
            'empty': empty_count
        }

    def copy_to(self, problem):
        new_part = Part()
        new_part.problem = problem
        new_part.description = self.description
        new_part.solution = self.solution
        new_part.validation = self.validation
        new_part.secret = self.secret
        new_part.save()
        return new_part
