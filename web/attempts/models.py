import json

from django.db import models
from simple_history.models import HistoricalRecords
from users.models import User
from utils import is_json_string_list


class AttemptQuerySet(models.QuerySet):
    def problem_set_statistics(self):
        success = {}
        for attempt in self.select_related("part__problem__problem_set"):
            part = attempt.part
            problem = part.problem
            problem_set = part.problem.problem_set
            if problem_set not in success:
                success[problem_set] = {}
            if problem not in success[problem_set]:
                success[problem_set][problem] = {}
            if part not in success[problem_set][problem]:
                success[problem_set][problem][part] = {
                    "valid": 0,
                    "invalid": 0,
                }
            if attempt.valid:
                success[problem_set][problem][part]["valid"] += 1
            else:
                success[problem_set][problem][part]["invalid"] += 1
        return success


class Attempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attempts")
    part = models.ForeignKey(
        "problems.Part", on_delete=models.CASCADE, related_name="attempts"
    )
    solution = models.TextField(blank=True)
    valid = models.BooleanField(default=False)
    feedback = models.TextField(default="[]", validators=[is_json_string_list])
    history = HistoricalRecords()
    submission_date = models.DateTimeField(auto_now=True)
    objects = AttemptQuerySet.as_manager()

    class Meta:
        unique_together = ("user", "part")

    def __str__(self):
        return "{} vs. @{:06d}: {}".format(
            self.user.username, self.part.pk, "valid" if self.valid else "invalid"
        )

    def feedback_list(self):
        return json.loads(json.loads(self.feedback))
