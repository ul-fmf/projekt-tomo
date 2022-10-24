from copy import deepcopy

from attempts.models import Attempt, HistoricalAttempt
from django.db import models
from django.db.models import Count
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
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
    institution = models.ForeignKey(Institution, related_name="institution")
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ["institution", "title"]

    def __str__(self):
        return "{} @{{{}}}".format(self.title, self.institution)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse

        return reverse("course_detail", args=[str(self.pk)])

    def recent_problem_sets(self, n=3):
        return self.problem_sets.reverse().filter(visible=True)[:n]

    def user_attempts(self, user):
        attempts = {}
        for attempt in user.attempts.filter(part__problem__problem_set__course=self):
            attempts[attempt.part_id] = attempt
        sorted_attempts = []
        for problem_set in self.problem_sets.all().prefetch_related("problems__parts"):
            problem_set_attempts = []
            prob_set_valid = prob_set_invalid = prob_set_empty = 0
            for problem in problem_set.problems.all():
                valid = invalid = empty = 0
                problem_attempts = [
                    attempts.get(part.pk) for part in problem.parts.all()
                ]
                for attempt in problem_attempts:
                    if attempt is None:
                        empty += 1
                    elif attempt.valid:
                        valid += 1
                    else:
                        invalid += 1
                problem_set_attempts.append(
                    (problem, problem_attempts, valid, invalid, empty)
                )
                prob_set_valid += valid
                prob_set_invalid += invalid
                prob_set_empty += empty
            sorted_attempts.append(
                (
                    problem_set,
                    problem_set_attempts,
                    prob_set_valid,
                    prob_set_invalid,
                    prob_set_empty,
                )
            )
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
        for problem_set in self.annotated_problem_sets:
            problem_set.percentage = problem_set.valid_percentage(user)
            if problem_set.percentage is None:
                problem_set.percentage = 0
            problem_set.grade = min(5, int(problem_set.percentage / 20) + 1)

    def annotate_for_teacher(self):
        students = self.observed_students()
        student_count = len(students)

        part_sets = Part.objects.filter(
            problem__problem_set__in=self.annotated_problem_sets
        )
        parts_count = (
            part_sets.values("problem__problem_set_id")
            .annotate(count=Count("problem__problem_set_id"))
            .order_by("count")
        )
        parts_dict = {}
        for part in parts_count:
            problem_set_id = part["problem__problem_set_id"]
            parts_dict[problem_set_id] = part["count"]

        attempts_full = Attempt.objects.filter(
            user__in=students,
            part__problem__problem_set__in=self.annotated_problem_sets,
        )
        attempts = attempts_full.values("valid", "part__problem__problem_set_id")
        attempts_dict = {}
        for attempt in attempts:
            problem_set_id = attempt["part__problem__problem_set_id"]
            if problem_set_id in attempts_dict:
                attempts_dict[problem_set_id]["submitted_count"] += 1
                attempts_dict[problem_set_id]["valid_count"] += (
                    1 if attempt["valid"] else 0
                )
            else:
                attempts_dict[problem_set_id] = {
                    "submitted_count": 1,
                    "valid_count": 1 if attempt["valid"] else 0,
                }

        for problem_set in self.annotated_problem_sets:
            part_count = (
                parts_dict[problem_set.id] if problem_set.id in parts_dict else 0
            )

            if problem_set.id in attempts_dict:
                submitted_count = attempts_dict[problem_set.id]["submitted_count"]
                valid_count = attempts_dict[problem_set.id]["valid_count"]
            else:
                submitted_count = 0
                valid_count = 0

            invalid_count = submitted_count - valid_count
            total_count = student_count * part_count

            if total_count:
                valid_percentage = int(100.0 * valid_count / total_count)
                invalid_percentage = int(100.0 * invalid_count / total_count)
            else:
                valid_percentage = 0
                invalid_percentage = 0

            empty_percentage = 100 - valid_percentage - invalid_percentage

            problem_set.valid = valid_percentage
            problem_set.invalid = invalid_percentage
            problem_set.empty = empty_percentage
            problem_set.grade = min(5, int(valid_percentage / 20) + 1)

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

    def student_success(self):
        students = self.observed_students()
        problem_sets = self.problem_sets.filter(visible=True)
        part_count = Part.objects.filter(problem__problem_set__in=problem_sets).count()
        attempts = Attempt.objects.filter(part__problem__problem_set__in=problem_sets)
        valid_attempts = (
            attempts.filter(valid=True).values("user").annotate(Count("user"))
        )
        all_attempts = attempts.values("user").annotate(Count("user"))

        def to_dict(attempts):
            attempts_dict = {}
            for val in attempts:
                attempts_dict[val["user"]] = val["user__count"]
            return attempts_dict

        valid_attempts_dict = to_dict(valid_attempts)
        all_attempts_dict = to_dict(all_attempts)
        for student in students:
            student.valid = valid_attempts_dict.get(student.pk, 0)
            student.invalid = all_attempts_dict.get(student.pk, 0) - student.valid
            student.empty = part_count - student.valid - student.invalid
        return students

    def duplicate(self):
        new_course = deepcopy(self)
        new_course.id = None
        new_course.title += " (copy)"
        new_course.save()
        for problem_set in self.problem_sets.all():
            problem_set.copy_to(new_course)
        return new_course

    def student_success_by_problem_set(self):
        """
        Function that will for each user calculate the solve rate for each problemset in the course. For example if the user
        has solved 3 problem parts out of 10 problem parts in the problemset, then his solve rate for that problemset
        would be 30%.

        Returns the dictionary of this form:
        {
            student : {
                problem_set : {
                    'valid' : float,
                    'invalid' : float,
                    'empty' : float
                }
            }
        }
        """

        students = self.observed_students()
        student_success_by_problemset = {student: {} for student in students}
        student_solve_rate_by_problemset = {student: {} for student in students}

        for problem_set in self.problem_sets.all().prefetch_related(
            "problems", "problems__parts"
        ):
            different_subtasks = 0
            for problem in problem_set.problems.all():
                for part in problem.parts.all():
                    different_subtasks += 1

            # In case there are no parts, we do not want to divide by 0
            if different_subtasks == 0:
                different_subtasks = 1

            for student in students:
                student_success_by_problemset[student][problem_set] = [
                    0,
                    0,
                ]  # Valid, invalid

            attempts = Attempt.objects.filter(
                part__problem__problem_set=problem_set, user__in=students
            )
            for attempt in attempts:
                if attempt.valid:
                    student_success_by_problemset[attempt.user][problem_set][0] += 1
                else:
                    student_success_by_problemset[attempt.user][problem_set][1] += 1

            for student in students:
                valid, invalid = student_success_by_problemset[student][problem_set]
                student_solve_rate_by_problemset[student][problem_set] = {
                    "valid": round(valid / different_subtasks, 2),
                    "invalid": round(invalid / different_subtasks, 2),
                    "empty": round(1 - (valid + invalid) / different_subtasks, 2),
                }

        return student_solve_rate_by_problemset

    def student_success_by_problemset_grouped_by_groups(self):
        """
        Function does the same as student_success_by_problem_set except that it groups students that are in the same group.
        Therefore we get a dictionary that will be easier to use inside a django template. An
        alternative would be to create django templatetags app and define filters with which we could
        access dictionary keys inside django templates.

        Returns a dictionary of the following form:

        {
            group : {
                student : {
                    problem_set : {
                        'valid' : float,
                        'invalid' : float,
                        'empty' : float
                    }
                }
            ]
        }
        """

        groups = self.groups.all()
        student_success = self.student_success_by_problem_set()

        student_sucess_by_groups = {}
        for group in groups:
            student_sucess_by_groups[group] = {}
            for student in group.students.all():
                student_sucess_by_groups[group][student] = student_success[student]

        return student_sucess_by_groups


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
    course = models.ForeignKey(Course, null=False, related_name="groups")
    students = models.ManyToManyField(User, blank=True, related_name="course_groups")

    def __str__(self):
        return self.title + " -- " + str(self.course)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse

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
    course = models.ForeignKey(Course, related_name="problem_sets")
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
        from django.core.urlresolvers import reverse

        return reverse("problem_set_detail", args=[str(self.pk)])

    def attempts_archive(self, user):
        files = [problem.attempt_file(user) for problem in self.problems.all()]
        archive_name = slugify(self.title)
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
        students = self.course.students.all()
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

        archive_name = "{0}-results".format(slugify(self.title))
        files = []

        bare_files = {}
        for problem in self.problems.all():
            folder = slugify(problem.title)
            for user in users.all():
                filename, contents = problem.marking_file(user)
                files.append(("{0}/{1}".format(folder, filename), contents))
                filename, contents = problem.bare_file(user)
                bare_files[filename] = bare_files.get(filename, "") + contents + "\n\n"

        for filename, contents in bare_files.items():
            files.append(("bare/{0}".format(filename), contents))

        for user, history in self.attempt_history().items():
            username = user.get_full_name() or user.username
            problem_slug = slugify(username).replace("-", "_")
            extension = "py"
            filename = "{0}.{1}".format(problem_slug, extension)
            contents = render_to_string(
                "history.py".format(extension),
                {
                    "history": history,
                },
            )
            files.append(("history/{0}".format(filename), contents))

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

    def student_statistics(self):
        students = self.course.observed_students()
        student_count = len(students)

        attempts = Attempt.objects.filter(
            part__problem__problem_set=self, user__in=students
        ).values("part_id", "valid")
        attempts_dict = {}
        for attempt in attempts:
            part_id = attempt["part_id"]
            if part_id in attempts_dict:
                attempts_dict[part_id]["valid_count"] += 1 if attempt["valid"] else 0
                attempts_dict[part_id]["submitted_count"] += 1
            else:
                attempts_dict[part_id] = {
                    "submitted_count": 1,
                    "valid_count": 1 if attempt["valid"] else 0,
                }

        statistics = []
        for problem in self.problems.all():
            parts = []
            for part in problem.parts.all():
                if part.id in attempts_dict:
                    submitted_count = attempts_dict[part.id]["submitted_count"]
                    valid_count = attempts_dict[part.id]["valid_count"]
                else:
                    submitted_count = 0
                    valid_count = 0

                invalid_count = submitted_count - valid_count
                empty_count = student_count - valid_count - invalid_count

                parts.append(
                    {
                        "anchor": part.anchor(),
                        "pk": part.pk,
                        "valid": valid_count,
                        "invalid": invalid_count,
                        "empty": empty_count,
                    }
                )
            statistics.append(
                {
                    "anchor": problem.anchor(),
                    "title": problem.title,
                    "pk": problem.pk,
                    "parts": parts,
                }
            )
        return statistics

    def valid_percentage(self, user):
        """
        Returns the percentage of parts (rounded to the nearest integer)
        of parts in this problem set for which the given user has a valid attempt.
        """
        number_of_all_parts = Part.objects.filter(problem__problem_set=self).count()
        number_of_valid_parts = user.attempts.filter(
            valid=True, part__problem__problem_set=self
        ).count()
        if number_of_all_parts == 0:
            return None
        else:
            return int(round(100.0 * number_of_valid_parts / number_of_all_parts))

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
