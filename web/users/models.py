from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    def can_edit_course(self, course):
        return self in course.teachers.all()

    def can_edit_problem_set(self, problem_set):
        return self.can_edit_course(problem_set.course)

    def can_edit_problem(self, problem):
        return self.can_edit_problem_set(problem.problem_set)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
