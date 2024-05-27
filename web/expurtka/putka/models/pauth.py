import expurtka.putka.config.settings as settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta
from expurtka.putka.models.groups import Group


class UserObjectPermission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="operms", on_delete=models.CASCADE
    )
    manage = models.BooleanField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey("content_type", "object_id")

    class Meta(TypedModelMeta):
        constraints = [
            models.UniqueConstraint(
                fields=("user", "manage", "content_type", "object_id"),
                name="%(app_label)s_%(class)s_unique",
            ),
        ]
        verbose_name = _("User object permission")
        verbose_name_plural = _("User object permissions")

    def __str__(self):
        return f"UserObjectPermission(user={self.user.username}, related_object={self.related_object}, manage={self.manage})"


class GroupObjectPermission(models.Model):
    group = models.ForeignKey(Group, related_name="operms", on_delete=models.CASCADE)
    manage = models.BooleanField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey("content_type", "object_id")

    class Meta(TypedModelMeta):
        constraints = [
            models.UniqueConstraint(
                fields=("group", "manage", "content_type", "object_id"),
                name="%(app_label)s_%(class)s_unique",
            ),
        ]
        verbose_name = _("Group object permission")
        verbose_name_plural = _("Group object permissions")

    def __str__(self):
        return f"GroupObjectPermission(group={self.group.name}, related_object={self.related_object}, manage={self.manage})"
