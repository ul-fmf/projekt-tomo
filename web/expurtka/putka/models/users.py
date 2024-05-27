import hashlib

import expurtka.putka.config.settings as settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta
from expurtka.putka.models.groups import Group


class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("Groups"),
        related_name="users",  # type: ignore[arg-type]
        help_text=_("The groups this user belongs to."),
    )


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE
    )
    lang = models.CharField(verbose_name=_("language"), max_length=2)
    country = models.CharField(verbose_name=_("country"), max_length=2)
    birthday = models.DateField(verbose_name=_("birthday"), null=True, blank=True)
    school = models.CharField(
        verbose_name=_("school"), max_length=200, blank=True, null=True
    )
    graduation_year = models.IntegerField(
        verbose_name=_("graduation year"), blank=True, null=True
    )
    forum_notify = models.IntegerField(
        choices=settings.FORUM_NOTIFY.choices,
        default=settings.FORUM_NOTIFY.recent_passive,
    )
    onsite_ip = models.CharField(max_length=39, null=True, blank=True)
    mentor = models.CharField(
        verbose_name=_("mentor"), max_length=200, null=True, blank=True
    )

    class Meta(TypedModelMeta):
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return f"Profile(user={self.user}, lang={self.lang})"

    def age(self):
        """Return current age in years."""
        return (
            (timezone.now().date() - self.birthday).days // 365
            if self.birthday
            else None
        )

    def avatar(self):
        """Return url to avatar."""
        h = hashlib.md5(self.user.email.lower().encode("utf-8")).hexdigest()
        return reverse("forums:avatar", args=(h,))
