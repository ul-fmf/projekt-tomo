from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        # In the forms, the __str__ method is used when showing model instances.
        return self.get_full_name()

    def save(self, *args, **kwargs):
        try:
            self.first_name = bytearray(self.first_name, "latin-1").decode("utf8")
            self.last_name = bytearray(self.last_name, "latin-1").decode("utf8")
        except UnicodeEncodeError:
            pass
        except UnicodeDecodeError:
            pass
        super(User, self).save(*args, **kwargs)

    def uses_shibboleth(self):
        try:
            return self.backend == "shibboleth.backends.ShibbolethRemoteUserBackend"
        except:
            return False

    def is_teacher(self, course):
        return self in course.teachers.all()

    def is_teacher_anywhere(self):
        return self.taught_courses.exists()

    def is_student(self, course):
        return self in course.students.all()

    def can_edit_course(self, course):
        return self.is_teacher(course)

    def can_edit_problem_set(self, problem_set):
        return self.can_edit_course(problem_set.course)

    def can_edit_problem(self, problem):
        return self.can_edit_problem_set(problem.problem_set)

    def can_view_course_attempts(self, course):
        return self.is_teacher(course)

    def can_view_course_groups(self, course):
        return self.is_teacher(course)

    def can_create_course_groups(self, course):
        return self.is_teacher(course)

    def can_update_course_groups(self, course):
        return self.is_teacher(course)

    def can_delete_course_groups(self, course):
        return self.is_teacher(course)

    def can_view_problem_set_attempts(self, problem_set):
        return self.can_view_course_attempts(problem_set.course)

    def is_favourite_course(self, course):
        return self.is_teacher(course) or self.is_student(course)

    def can_view_course(self, course):
        return True

    def can_view_problem_set(self, problem_set):
        return self.can_view_course(problem_set.course) and (
            problem_set.visible or self.is_teacher(problem_set.course)
        )

    def can_view_problem(self, problem):
        return self.can_view_problem_set(problem.problem_set)

    def can_view_problem_solution(self, problem, student):
        return self.can_view_problem(problem) and (
            self == student or self.is_teacher(problem.problem_set.course)
        )

    def can_view_course_statistics(self, course):
        return self.is_teacher(course)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


User._meta.get_field("username").max_length = 70
User._meta.get_field("first_name").max_length = 70
User._meta.get_field("last_name").max_length = 70
