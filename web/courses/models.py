from copy import deepcopy

from attempts.models import Attempt, HistoricalAttempt
from attempts.outcome import Outcome
from django.db import models
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from problems.models import Part
from taggit.managers import TaggableManager
from users.models import User
from utils.models import OrderWithRespectToMixin


class Institution(models.Model):
    name = models.CharField(max_length=140)

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    students = models.ManyToManyField(
        User, blank=True, related_name="courses", through="StudentEnrollment"
    )
    teachers = models.ManyToManyField(User, blank=True, related_name="taught_courses")
    institution = models.ForeignKey(
        Institution, on_delete=models.PROTECT, related_name="institution"
    )
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ["institution", "title"]

    def __str__(self):
        return "{} @{{{}}}".format(self.title, self.institution)

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("course_detail", args=[str(self.pk)])

    def recent_problem_sets(self, n=3):
        return self.problem_sets.reverse().filter(visible=True)[:n]

    def user_attempts(self, user):
        """This function ignores problem visibility, because it assumes it is only
        called from problems/models.py:marking_file() by a teacher user."""
        parts = Part.objects.filter(problem__problem_set__course=self)
        users = User.objects.filter(id=user.id)
        outcomes = Outcome.group_dict(parts, users, ("problem",), ())
        attempts = {}
        for attempt in user.attempts.filter(part__problem__problem_set__course=self):
            attempts[attempt.part_id] = attempt
        sorted_attempts = []
        for problem_set in self.problem_sets.all().prefetch_related("problems__parts"):
            problem_set.outcome = Outcome()
            problem_set.attempts = []
            for problem in problem_set.problems.all():
                problem.outcome = outcomes[(problem.id,)]
                problem.attempts = [
                    attempts.get(part.pk) for part in problem.parts.all()
                ]
                problem_set.attempts.append(problem)
                problem_set.outcome += problem.outcome
            sorted_attempts.append(problem_set)
        return sorted_attempts

    def prepare_annotated_problem_sets(self, user):
        self.is_taught = user.can_edit_course(self)
        self.is_favourite = user.is_favourite_course(self)
        self.annotated_problem_sets = []
        for problem_set in self.problem_sets.all():
            if user.can_view_problem_set(problem_set):
                self.annotated_problem_sets.append(problem_set)

    def annotate(self, user):
        if self.is_taught:
            self.annotate_for_teacher()
        else:
            self.annotate_for_user(user)

    def annotate_for_user(self, user):
        parts = Part.objects.filter(
            problem__problem_set__course=self, problem__visible=True
        )
        users = User.objects.filter(id=user.id)
        outcomes = Outcome.group_dict(parts, users, ("problem__problem_set",), ())
        for problem_set in self.annotated_problem_sets:
            problem_set.outcome = outcomes.get((problem_set.id,), Outcome(0, 0, 1))

    def annotate_for_teacher(self):
        parts = Part.objects.filter(
            problem__problem_set__course=self, problem__visible=True
        )
        users = self.observed_students()
        outcomes = Outcome.group_dict(parts, users, ("problem__problem_set",), ())
        for problem_set in self.annotated_problem_sets:
            problem_set.outcome = outcomes.get((problem_set.id,), Outcome(0, 0, 1))

    def enroll_student(self, user):
        enrollment = StudentEnrollment(course=self, user=user)
        enrollment.save()

    def unenroll_student(self, user):
        enrollment = StudentEnrollment.objects.get(course=self, user=user)
        enrollment.delete()

    def promote_to_teacher(self, user):
        self.unenroll_student(user)
        self.teachers.add(user)

    def demote_to_student(self, user):
        self.enroll_student(user)
        self.teachers.remove(user)

    def toggle_observed(self, user):
        enrollment = StudentEnrollment.objects.get(course=self, user=user)
        enrollment.observed = not enrollment.observed
        enrollment.save()

    def observed_students(self):
        return User.objects.filter(
            studentenrollment__course=self, studentenrollment__observed=True
        ).order_by("first_name")

    def student_outcome(self):
        parts = Part.objects.filter(
            problem__problem_set__course=self, problem__problem_set__visible=True
        )
        users = self.observed_students()
        outcomes = Outcome.group_dict(parts, users, (), ("id",))
        annotated_users = list(users)
        for user in annotated_users:
            user.outcome = outcomes[(user.id,)]
        return annotated_users

    def duplicate(self):
        new_course = deepcopy(self)
        new_course.id = None
        new_course.title += " (copy)"
        new_course.save()
        for problem_set in self.problem_sets.all():
            problem_set.copy_to(new_course)
        return new_course


class StudentEnrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    observed = models.BooleanField(default=True)

    class Meta:
        ordering = ["user", "course"]
        unique_together = ("course", "user")


class CourseGroup(models.Model):
    """
    With this model we will be able to create subgroups of students within some course.
    """

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    course = models.ForeignKey(
        Course, null=False, on_delete=models.CASCADE, related_name="groups"
    )
    students = models.ManyToManyField(User, blank=True, related_name="course_groups")

    class Meta:
        ordering = ["title", "description"]

    def __str__(self):
        return self.title + " -- " + str(self.course)

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("course_groups", args=[str(self.course.pk)])

    def list_all_members(self):
        return self.students.all().order_by("first_name")


class ProblemSet(OrderWithRespectToMixin, models.Model):
    PROBLEM_HIDDEN = "P"
    SOLUTION_HIDDEN = "H"
    SOLUTION_VISIBLE_WHEN_SOLVED = "S"
    SOLUTION_VISIBLE = "V"
    SOLUTION_VISIBILITY_CHOICES = (
        (PROBLEM_HIDDEN, _("Problem descriptions and official solutions are hidden")),
        (SOLUTION_HIDDEN, _("Official solutions are hidden")),
        (SOLUTION_VISIBLE_WHEN_SOLVED, _("Official solutions are visible when solved")),
        (SOLUTION_VISIBLE, _("Official solutions are visible")),
    )
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name="problem_sets"
    )
    title = models.CharField(max_length=70, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    visible = models.BooleanField(default=False, verbose_name=_("Visible"))
    solution_visibility = models.CharField(
        max_length=20,
        verbose_name=_("Solution visibility"),
        choices=SOLUTION_VISIBILITY_CHOICES,
        default=SOLUTION_VISIBLE_WHEN_SOLVED,
    )
    tags = TaggableManager(blank=True)

    class Meta:
        order_with_respect_to = "course"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("problem_set_detail", args=[str(self.pk)])

    @property
    def visible_problems(self):
        return self.problems.filter(visible=True)

    def attempts_archive(self, user):
        if user.can_edit_problem_set(self):
            files = [problem.attempt_file(user) for problem in self.problems.all()]
        else:
            files = [problem.attempt_file(user) for problem in self.visible_problems]
        archive_name = slugify(self.title)
        return archive_name, files

    def solutions_archive(self):
        files = [problem.solution_file() for problem in self.problems.all()]
        archive_name = "{0}-solution".format(slugify(self.title))
        return archive_name, files

    def edit_archive(self, user):
        files = [problem.edit_file(user) for problem in self.problems.all()]
        archive_name = "{0}-edit".format(slugify(self.title))
        return archive_name, files

    def attempt_history(self):
        user_attempts = {}
        attempts = (
            HistoricalAttempt.objects.filter(part__problem__problem_set=self)
            .select_related("part__problem", "user")
            .distinct()
            .order_by("history_date")
        )
        for attempt in attempts:
            user_attempts.setdefault(attempt.user, []).append(attempt)
        return user_attempts

    def results_archive(self, user):
        user_ids = set()
        attempt_dict = {}
        attempts = Attempt.objects.filter(part__problem__problem_set=self)
        for attempt in attempts:
            user_id = attempt.user_id
            user_ids.add(user_id)
            user_attempts = attempt_dict.get(user_id, {})
            user_attempts[attempt.part_id] = attempt
            attempt_dict[user_id] = user_attempts
        users = User.objects.filter(id__in=user_ids)

        archive_name = f"{slugify(self.title)}-results"
        files = []

        bare_files = {}
        for problem in self.problems.all():
            folder = slugify(problem.title)
            for user in users.all():
                filename, contents = problem.marking_file(user)
                files.append((f"{folder}/{filename}", contents))
                filename, contents = problem.bare_file(user)
                bare_files[filename] = bare_files.get(filename, "") + contents + "\n\n"

        for filename, contents in bare_files.items():
            files.append((f"bare/{filename}", contents))

        for user, history in self.attempt_history().items():
            username = user.get_full_name() or user.username
            problem_slug = slugify(username).replace("-", "_")
            extension = "py"
            filename = f"{problem_slug}.{extension}"
            contents = render_to_string(
                f"history.{extension}",
                {
                    "history": history,
                },
            )
            files.append((f"history/{filename}", contents))

        users = []
        for user in User.objects.filter(id__in=user_ids).order_by("last_name"):
            user_attempts = []
            for problem in self.problems.all():
                for part in problem.parts.all():
                    user_attempts.append(attempt_dict[user.id].get(part.id))
            users.append((user, user_attempts))

        spreadsheet_filename = "{0}.csv".format(self.title)
        spreadsheet_contents = render_to_string(
            "results.csv", {"problem_set": self, "users": users}
        )
        files.append((spreadsheet_filename, spreadsheet_contents))
        return archive_name, files

    def outcomes_statistics(self, outcomes):
        statistics = []
        for problem in self.problems.prefetch_related("parts"):
            parts = []
            for part in problem.parts.all():
                parts.append(
                    {
                        "anchor": part.anchor(),
                        "pk": part.pk,
                        "outcome": outcomes[(part.pk,)],
                    }
                )
            statistics.append(
                {
                    "anchor": problem.anchor(),
                    "title": problem.title,
                    "pk": problem.pk,
                    "parts": parts,
                    "visible": problem.visible,
                }
            )
        return statistics

    def single_student_statistics(self, student):
        students = User.objects.filter(id=student.id)
        parts = Part.objects.filter(problem__problem_set=self, problem__visible=True)
        outcomes = Outcome.group_dict(parts, students, ("id",), ())
        return self.outcomes_statistics(outcomes)

    def all_students_statistics(self):
        students = self.course.observed_students()
        parts = Part.objects.filter(problem__problem_set=self)
        outcomes = Outcome.group_dict(parts, students, ("id",), ())
        return self.outcomes_statistics(outcomes)

    def toggle_visible(self):
        self.visible = not self.visible
        self.save()

    def toggle_solution_visibility(self):
        next_state = {
            self.PROBLEM_HIDDEN: self.SOLUTION_HIDDEN,
            self.SOLUTION_HIDDEN: self.SOLUTION_VISIBLE_WHEN_SOLVED,
            self.SOLUTION_VISIBLE_WHEN_SOLVED: self.SOLUTION_VISIBLE,
            self.SOLUTION_VISIBLE: self.PROBLEM_HIDDEN,
        }
        self.solution_visibility = next_state[self.solution_visibility]
        self.save()

    def copy_to(self, course):
        new_problem_set = deepcopy(self)
        new_problem_set.id = None
        new_problem_set.course = course
        new_problem_set.save()
        for problem in self.problems.all():
            problem.copy_to(new_problem_set)
        return new_problem_set
