import json
from copy import deepcopy

from attempts.outcome import Outcome
from django.conf import settings
from django.core import signing
from django.db import models
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager
from utils import is_json_string_list, truncate
from utils.models import OrderWithRespectToMixin


class Problem(models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    history = HistoricalRecords()
    tags = TaggableManager(blank=True)
    language = models.CharField(
        max_length=8,
        choices=(("python", "Python 3"), ("octave", "Octave/Matlab"), ("r", "R")),
        default="python",
    )
    EXTENSIONS = {"python": "py", "octave": "m", "r": "r"}
    MIMETYPES = {"python": "text/x-python", "octave": "text/x-octave", "r": "text/x-R"}

    def __str__(self):
        return self.title

    @property
    def guarded_description(self):
        return (
            "Navodila so napisana na listu"
            if self.problem_set.solution_visibility == self.problem_set.PROBLEM_HIDDEN
            else self.description
        )

    def get_absolute_url(self):
        return "{}#{}".format(self.problem_set.get_absolute_url(), self.anchor())

    def anchor(self):
        return f"problem-{self.pk}"

    @property
    def slug(self):
        return slugify(self.title).replace("-", "_")

    def solution_file(self):
        parts = [(part, part.solution) for part in self.parts.all()]
        problem_slug = slugify(self.title).replace("-", "_")
        extension = self.EXTENSIONS[self.language]
        filename = f"{problem_slug}_solution.{extension}"
        contents = render_to_string(
            f"{self.language}/solution.{extension}",
            {
                "problem": self,
                "parts": parts,
            },
        )
        return filename, contents


    def edit_file(self, user):
        """This function ignores problem visibility because it assumes its
        called only from courses/models.py:edit_archive() by a teacher user
        """
        authentication_token = Token.objects.get(user=user)
        url = settings.SUBMISSION_URL + reverse("problems-submit")
        problem_slug = slugify(self.title).replace("-", "_")
        filename = f"{problem_slug}_edit.{self.EXTENSIONS[self.language]}"
        contents = render_to_string(
            f"{self.language}/edit.{self.EXTENSIONS[self.language]}",
            {
                "problem": self,
                "submission_url": url,
                "authentication_token": authentication_token,
            },
        )
        return filename, contents

    def duplicate(self):
        new_problem = deepcopy(self)
        new_problem.pk = None
        new_problem.save()
        for part in self.parts.all():
            part.copy_to(new_problem)
        return new_problem

    def content_type(self):
        return self.MIMETYPES[self.language]
    
    def extension(self):
        return self.EXTENSIONS[self.language]


class Part(OrderWithRespectToMixin, models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="parts")
    description = models.TextField(blank=True)
    template = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    validation = models.TextField(blank=True)
    secret = models.TextField(default="[]", validators=[is_json_string_list])
    history = HistoricalRecords()

    class Meta:
        order_with_respect_to = "problem"

    def __str__(self):
        return "@{0:06d} ({1})".format(self.pk, truncate(self.description))

    @property
    def guarded_description(self):
        return (
            "Navodila so napisana na listu"
            if self.problem.problem_set.solution_visibility
            == self.problem.problem_set.PROBLEM_HIDDEN
            else self.description
        )

    def get_absolute_url(self):
        return "{}#{}".format(self.problem_set.get_absolute_url(), self.anchor())

    def anchor(self):
        return "part-{}".format(self.pk)

    def check_secret(self, secret):
        """
        Checks whether a submitted secret corresponds to the official one.

        The function accepts a secret (list of strings) and returns the pair:
        True, None -- if secret matches the official one
        False, None -- if secret has an incorrect length
        False, i -- if secret first differs from the official one at index i
        """
        official_secret = json.loads(self.secret)
        if len(official_secret) != len(secret):
            return False, None
        for i in range(len(secret)):
            if secret[i] != official_secret[i]:
                return False, i
        return True, None

    def copy_to(self, problem):
        new_part = deepcopy(self)
        new_part.pk = None
        new_part.problem = problem
        new_part.save()
        return new_part

    def attempt_token(self, user):
        return signing.dumps(
            {
                "part": self.pk,
                "user": user.pk,
            }
        )
