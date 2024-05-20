from typing import TYPE_CHECKING, Dict, Type

import expurtka.putka.config.settings as settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta
from expurtka.putka.alert_types import AlertBase, AlertPermissionCheckResult, AlertRenderInfo
from expurtka.putka.helpers import ClassPath
# from ui.core.serverpush import dispatcher

if TYPE_CHECKING:
	from expurtka.putka.models.results import Upload
	from expurtka.putka.models.users import User as UserType
	from expurtka.putka.models.forums import Thread


class Alert(models.Model):
	"""General purpose notification shown to the user."""

	created = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='User who should be shown the alert.')
	type = models.PositiveSmallIntegerField(verbose_name='Alert type', choices=settings.ALERT_TYPES.choices)

	# Object that the alert is related to.
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	related_object = GenericForeignKey('content_type', 'object_id')

	# Permissions for alerts are sometimes evaluated lazily on display;
	# if this is True, the thread pointed to by the alert is visible to the user.
	# If the permission check fails, the alert is deleted immediately after the permission check.
	perms_checked = models.BooleanField(default=False)

	class Meta(TypedModelMeta):
		constraints = [
			models.UniqueConstraint(fields=['user', 'type', 'content_type', 'object_id'], name='unique_alert')
		]
		verbose_name = _("Alert")
		verbose_name_plural = _("Alerts")

	def __str__(self):
		return f"Alert(pk={self.pk}, user={self.user}, type={settings.ALERT_TYPES(self.type).name}, object_id={self.object_id})"

	_ALERT_SUBCLASS_MAP: Dict[int, Type[AlertBase]] = {
		k: ClassPath(v)() for k, v in settings.ALERT_SUBCLASS_MAP.items()
	}

	# @staticmethod
	# def ajax_wake():
	# 	dispatcher.notify_for_model(Alert, dispatcher.Event.UPDATED)

	@staticmethod
	def for_thread_activity(*, user: 'UserType', thread: 'Thread') -> 'Alert':
		return Alert(user=user, type=settings.ALERT_TYPES.thread_activity, related_object=thread.concrete())

	@staticmethod
	def for_manual_grading(*, user: 'UserType', upload: 'Upload') -> 'Alert':
		return Alert(user=user, type=settings.ALERT_TYPES.manual_grading, related_object=upload, perms_checked=True)

	@staticmethod
	def for_suspicious_upload(*, user: 'UserType', upload: 'Upload') -> 'Alert':
		return Alert(user=user, type=settings.ALERT_TYPES.pragma, related_object=upload, perms_checked=True)

	@staticmethod
	def for_internal_error(*, user: 'UserType', upload: 'Upload') -> 'Alert':
		return Alert(user=user, type=settings.ALERT_TYPES.internal_error, related_object=upload, perms_checked=True)

	def get_absolute_url(self) -> str:
		return reverse('alerts:dispatch', args=(self.id,))

	def check_object(self) -> bool:
		"""Check whether the object pointed to exists."""
		if self.related_object is None:
			return False
		return True

	def _concrete(self) -> AlertBase:
		if not self.check_object():
			raise Alert.DoesNotExist
		return Alert._ALERT_SUBCLASS_MAP[self.type](self)

	# Duplicate the interface of AlertBase to make it public.
	# Could be done with metaclasses, but it's not really worth it.
	@cached_property
	def render(self) -> AlertRenderInfo:
		return self._concrete().render()

	def validate_perms_or_delete(self) -> AlertPermissionCheckResult:
		return self._concrete().validate_perms_or_delete()

	def redirect_url(self) -> str:
		return self._concrete().redirect_url()

	def delete_on_click(self) -> bool:
		return self._concrete().delete_on_click()
