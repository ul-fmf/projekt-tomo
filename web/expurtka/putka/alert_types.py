"""
Implementation of specific alert types.

The whole module is private and should be considered an implementation detail of the Alert model.
Depending on the type of the Alert model, different concrete classes defined in this module will
be used, as defined in the type-to-class map in the Alert model. The base class only serves to
guarantee the same interface across various alert classes.
"""


from abc import ABC, abstractmethod
from dataclasses import dataclass

from django.urls import reverse
from django.utils.translation import gettext as _

from expurtka.putka.helpers import preferred_lang


@dataclass(slots=True, frozen=True)
class AlertRenderInfo:
	title: str
	url_title: str


@dataclass(slots=True, frozen=True)
class AlertPermissionCheckResult:
	has_permission: bool
	should_update: bool


class AlertBase(ABC):
	"""Defines the interface all alerts are required to implement."""

	def __init__(self, alert):
		self.alert = alert

	def validate_perms_or_delete(self) -> AlertPermissionCheckResult:
		"""Return True if permission check passed."""
		return AlertPermissionCheckResult(has_permission=self.alert.perms_checked, should_update=False)

	def delete_on_click(self) -> bool:
		"""Delete the alert when it's clicked or not."""
		return True

	@abstractmethod
	def redirect_url(self) -> str:
		return NotImplemented

	def render(self) -> AlertRenderInfo:
		return AlertRenderInfo(
			title=self._title(),
			url_title=self._url_title()
		)

	@abstractmethod
	def _title(self) -> str:
		return NotImplemented

	@abstractmethod
	def _url_title(self) -> str:
		return NotImplemented


class _ThreadActivityAlert(AlertBase):
	def _title(self):
		return _("Forum: new message")

	def _url_title(self):
		thread = self.alert.related_object
		return thread.best_title(preferred_lang(self.alert.user))

	def validate_perms_or_delete(self):
		"""
		Return True if permission check passed.

		Otherwise, the alert is deleted, and False is returned.
		"""
		if self.alert.perms_checked:
			return AlertPermissionCheckResult(has_permission=True, should_update=False)
		thread = self.alert.related_object
		if not self.alert.user.has_perm('view', thread):
			return AlertPermissionCheckResult(has_permission=False, should_update=False)

		self.alert.perms_checked = True
		return AlertPermissionCheckResult(has_permission=True, should_update=True)

	def redirect_url(self):
		thread = self.alert.related_object
		return reverse('forums:show-thread', args=(thread.type(), thread.forum_url(), thread.uid()))


class _UploadAlert(AlertBase):
	def _url_title(self):
		upload = self.alert.related_object
		return _("Upload #{id} by {username}").format(id=upload.id, username=upload.user.username)

	def redirect_url(self):
		return reverse('results:detail', args=(self.alert.object_id,))

	def delete_on_click(self) -> bool:
		return False


class _ManualGradingAlert(_UploadAlert):
	def _title(self):
		return _("Manual grading")


class _SuspiciousUploadAlert(_UploadAlert):
	def _title(self):
		return _("Suspicious upload")

	def delete_on_click(self) -> bool:
		return True


class _InternalErrorAlert(_UploadAlert):
	def _title(self):
		return _("Internal error")
