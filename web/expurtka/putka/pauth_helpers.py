import random
from typing import Generic, Protocol, Type, TypeVar

import expurtka.putka.config.settings as settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import Exists, Model, OuterRef, QuerySet
from expurtka.putka.models.pauth import GroupObjectPermission, UserObjectPermission

_PASS_CHARSET = "23456789qwertuipasdfghjkxcvbnmQWERTUPASDFGHJKLXCVBNM"


def generate_password(length=7) -> str:
    return "".join(random.choice(_PASS_CHARSET) for _ in range(length))


def superuser_required(
    view_func=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url=settings.LOGIN_URL,
):
    """Check that the user is logged in and is a superuser, raising PermissionDenied if not."""

    def test(u):
        if not (u.is_active and u.is_superuser):
            raise PermissionDenied
        return True

    actual_decorator = user_passes_test(
        test, login_url=login_url, redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def staff_required(
    view_func=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url=settings.LOGIN_URL,
):
    """Check that the user is logged in and is a staff member, raising PermissionDenied if not.

    Django's built-in @staff_member_required only redirects to admin login and has no option
    to raise PermissionDenied.
    """

    def test(u):
        if not (u.is_active and u.is_staff):
            raise PermissionDenied
        return True

    actual_decorator = user_passes_test(
        test, login_url=login_url, redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


M = TypeVar("M", bound=Model)


class QuerySetProtocol(Protocol[M]):
    model: Type[M]

    def filter(self, *args, **kwargs) -> QuerySet[M]:
        ...


class PermissionQuerySetMixin(Generic[M]):
    def only_if_explicit_perm(
        self: QuerySetProtocol[M], user_id: int, manage: bool
    ) -> QuerySet[M]:
        ct = ContentType.objects.get_for_model(self.model)
        manage_q = {"manage": manage} if manage else {}
        return self.filter(
            Exists(
                UserObjectPermission.objects.filter(
                    user_id=user_id,
                    object_id=OuterRef("id"),
                    content_type=ct,
                    **manage_q,
                )
            )
            | Exists(
                GroupObjectPermission.objects.filter(
                    group__users=user_id,
                    object_id=OuterRef("id"),
                    content_type=ct,
                    **manage_q,
                )
            )
        )
