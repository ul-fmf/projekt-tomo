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
    
    def can_view_course(self, course):
        return (self in course.teachers.all() or self in course.students.all())
    
    def can_view_problem_set(self, problem_set):
        return self.can_view_course(problem_set.course)
    
    def can_view_problem(self, problem):
        return self.can_view_problem_set(problem.problem_set)
    
#     def can_view_solutions(self, part):
#         problem_set = part.problem.problem_set
#         problem_set_visibility = problem_set.solution_visibility
#         if problem_set_visibility == problem_set.SOLUTION_VISIBLE:
#             return True 
#         elif problem_set_visibility == problem_set.SOLUTION_VISIBLE_WHEN_SOLVED:
#             #check if user's attempt for this part exists
#             try:
#                 attempt = part.attempts.get(user=self)
#                 #check if user's attempt for this part is accepted
#                 return attempt.is_valid
#             except ObjectDoesNotExist:
#                 return False
#             return attempt.is_valid()
#         else:
#             return self.can_edit_problem(part.problem)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
