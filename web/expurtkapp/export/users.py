import attempts.models as tomo_attempts
import users.models as tomo
from django.db.models import Q


def course_users(courses, include_attempts):
    """Students and teachers of the given courses, and, if attempts are exported,
    all users that submitted an attempt in them."""
    condition = Q(pk__in=courses.values("students")) | Q(
        pk__in=courses.values("teachers")
    )
    if include_attempts:
        condition |= Q(
            pk__in=tomo_attempts.Attempt.objects.filter(
                part__problem__problem_set__course__in=courses
            ).values("user")
        )
    return tomo.User.objects.filter(condition)


def export_users(users):
    return [
        {
            "pk": user.pk,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "date_joined": user.date_joined.strftime("%Y-%m-%d"),
        }
        for user in users
    ]


def export_all(users):
    return export_users(users)
