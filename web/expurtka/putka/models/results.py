import re
from typing import TYPE_CHECKING, List, Optional, TypedDict

import expurtka.putka.config.settings as settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Prefetch
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta
from expurtka.putka.models.alerts import Alert
from expurtka.putka.models.contests import Contest
from expurtka.putka.models.tasks import File, Task
from expurtka.putka.results_helpers import COMPILE_ERROR_TEXT, upload_solved_q_expr

# from ui.core.wiki.helpers import best_title_subquery

if TYPE_CHECKING:
    from django.utils.functional import _StrOrPromise as StrOrPromise


INPUT_FILENAME_REGEX = re.compile(r"(.*\.(?:pub)?)in")


class UploadBase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lang = models.IntegerField(choices=settings.PROG_LANGS.choices)
    filename = models.TextField()
    source = models.BinaryField()
    upload_time = models.DateTimeField(default=timezone.now, db_index=True)
    # processing
    status = models.IntegerField(
        choices=settings.UPLOAD_STATUS.choices, default=settings.UPLOAD_STATUS.waiting
    )  # Processing stage.
    mgr_status = models.IntegerField(
        default=-1, null=True, blank=True
    )  # Manager only, for queuing. UI does not touch.
    preparation_status = models.IntegerField(
        choices=settings.JAILRUN_STATUS.choices, null=True, blank=True
    )  # compile job
    preparation_output = models.BinaryField(
        null=True, blank=True
    )  # compile job stderr+stdout
    system_output = models.BinaryField(
        null=True, blank=True
    )  # testscript stdout+stderr (e.g. stack trace in event of tester failure)
    tester_signature = models.CharField(max_length=50, null=True, blank=True)

    class Meta(TypedModelMeta):
        abstract = True

    @cached_property
    def pretty_lang(self) -> str:
        return settings.PROG_LANGS(self.lang).label


class UploadQuerySet(models.QuerySet):
    SOLVED_Q = upload_solved_q_expr()

    def with_contests(self) -> "UploadQuerySet":
        return self.prefetch_related(
            Prefetch(
                "contests",
                queryset=Contest.objects.only("title", "url"),
                to_attr="contest_list",
            )
        )

    # def with_task_titles(self, pref_lang):
    # 	return self.annotate(best_title=best_title_subquery(pref_lang, 'task_id', Task))

    def solved(self) -> "UploadQuerySet":
        return self.filter(self.SOLVED_Q)


class Upload(UploadBase):
    # initial data
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    # backend output
    points = models.IntegerField(null=True, blank=True)
    max_points = models.IntegerField(null=True, blank=True)
    # Aggregate status of
    # all testcases. Mostly for caching since it could be computed on the fly, but also to support
    # marking up manually detected presentation errors.
    agg_status = models.IntegerField(
        choices=settings.JAILRUN_STATUS.choices, null=True, blank=True
    )
    reviewer_comment = models.TextField(
        null=True, blank=True
    )  # a manually entered comment, usually for manual grading
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="reviewed",
        on_delete=models.SET_NULL,
    )
    is_official_solution = models.BooleanField(default=False)

    # GenericRelation must be present to support cascading deletion of alerts when a post is deleted.
    alerts = GenericRelation(Alert)

    objects = UploadQuerySet.as_manager()

    contest_list: Optional[List["Contest"]]
    skip_suspicious_recheck: bool
    serverpush_skip_signal: bool

    class Meta(TypedModelMeta):
        ordering = ["-upload_time"]

    def is_solved(self) -> bool:
        return (
            self.status == settings.UPLOAD_STATUS.done
            and self.preparation_status == settings.JAILRUN_STATUS.OK
            and self.agg_status == settings.JAILRUN_STATUS.OK
            and self.points == self.max_points
        )

    def __str__(self) -> str:
        info: "StrOrPromise"
        if self.status != settings.UPLOAD_STATUS.done:
            info = settings.UPLOAD_STATUS(self.status).label
        elif self.preparation_status != settings.JAILRUN_STATUS.OK:
            info = COMPILE_ERROR_TEXT
        else:
            assert self.agg_status is not None
            info = settings.JAILRUN_STATUS(self.agg_status).name
        if self.points is not None:
            info += f", {self.points}/{self.max_points}"
        return f"Upload #{self.id} ({info})"

    def public_testcases_with_files(self) -> List["TestCase"]:
        """Match each public test case with its input and output files."""
        return self._augment_testcases_with_files(
            list(self.testcase_set.filter(name__endswith=".pubin"))
        )

    def testcases_with_files(self) -> List["TestCase"]:
        """Match each test case with its input and output files."""
        return self._augment_testcases_with_files(list(self.testcase_set.all()))

    def _augment_testcases_with_files(
        self, test_cases: List["TestCase"]
    ) -> List["TestCase"]:
        test_files = {
            f.filename: f
            for f in self.task.file_set.inputs_and_outputs().only("filename", "task_id")
        }  # 'task_id' needed for the ORM
        for test_case in test_cases:
            fn_in = test_case.name
            fn_out = INPUT_FILENAME_REGEX.sub(r"\1out", fn_in)
            test_case.data_files = {
                "input": test_files.get(fn_in),
                "output": test_files.get(fn_out),
            }
        return test_cases

    def save_as_ok_with_no_points(self):
        self.points = 0
        self.max_points = 0
        self.status = settings.UPLOAD_STATUS.done
        self.preparation_status = settings.JAILRUN_STATUS.OK
        self.agg_status = settings.JAILRUN_STATUS.OK
        self.save()


class Stat(models.Model):
    run_status = models.IntegerField(
        choices=settings.JAILRUN_STATUS.choices, null=True, blank=True
    )
    time = models.FloatField(null=True, blank=True)
    memory = models.FloatField(null=True, blank=True)
    tasks = models.IntegerField(null=True, blank=True)
    exit_code = models.IntegerField(null=True, blank=True)

    class Meta(TypedModelMeta):
        abstract = True


class TestCase(Stat):
    name = models.CharField(
        max_length=100,
        help_text=_("Input filename (by convention) or another descriptive name"),
    )
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE)
    points = models.IntegerField()
    max_points = models.IntegerField()
    user_output = models.BinaryField(null=True, blank=True)
    user_output_line = models.IntegerField(
        null=True,
        blank=True,
        help_text=_(
            "Line number of the user output file where to begin showing the data diff."
        ),
    )
    official_output = models.BinaryField(null=True, blank=True)
    official_output_line = models.IntegerField(
        null=True,
        blank=True,
        help_text=_(
            "Line number of the official output file where to begin showing the data diff."
        ),
    )
    user_stderr = models.BinaryField(null=True, blank=True)

    class DataFile(TypedDict):
        input: Optional[File]
        output: Optional[File]

    data_files: DataFile

    class Meta(TypedModelMeta):
        ordering = ["id"]
        verbose_name = _("Test case")
        verbose_name_plural = _("Test cases")

    def __str__(self):
        return f"TestCase(id={self.id}, name={self.name}, upload_id={self.upload_id})"

    def status(self) -> Optional[int]:
        if (
            self.run_status == settings.JAILRUN_STATUS.OK
            and self.points != self.max_points
        ):
            return settings.JAILRUN_STATUS.WA
        return self.run_status

    def pretty_score(self) -> SafeString:
        is_public = self.name.endswith(".pubin")
        return mark_safe(
            '<span class="%s">%d/%d</span>'
            % (
                "fail"
                if (self.points == 0 and self.max_points > 0)
                else "partial"
                if (self.points < self.max_points)
                else "ok",
                0
                if is_public
                else self.points,  # Print zeros to indicate that samples don't count towards the score.
                0 if is_public else self.max_points,
            )
        )


class UserTest(Stat, UploadBase):
    user_input = models.BinaryField()
    user_output = models.BinaryField(null=True, blank=True)
    user_stderr = models.BinaryField(null=True, blank=True)

    class Meta(TypedModelMeta):
        ordering = ["-upload_time"]

    def is_compile_error(self):
        return (
            self.preparation_status is not None
            and self.preparation_status != settings.JAILRUN_STATUS.OK
        )

    def is_done(self):
        return self.run_status is not None
