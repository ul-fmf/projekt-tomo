import datetime
import json
import logging
from typing import Optional

import expurtka.putka.config.settings as settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.db import DataError, models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta
from expurtka.putka.config.settings.enums import CONTEST_STATE
from expurtka.putka.slugify import PUTKA_SLUG_VALIDATOR
from expurtka.putka.pauth_helpers import PermissionQuerySetMixin
from expurtka.putka.models.pauth import GroupObjectPermission, UserObjectPermission

logger = logging.getLogger(__name__)  # noqa


class ContestQuerySet(PermissionQuerySetMixin, models.QuerySet):
	def ongoing(self) -> 'ContestQuerySet':
		return self.filter(actual_start__isnull=False, actual_end__isnull=True)

	def ongoing_for_user(self, user: AbstractUser) -> 'ContestQuerySet':
		return self.ongoing().filter(
			contestants=user,
			contestant__disqualified=False,
		)

	def started(self) -> 'ContestQuerySet':
		return self.filter(actual_start__isnull=False)


class Contest(models.Model):
	title = models.CharField(max_length=50, verbose_name=_("Title"))
	url = models.SlugField(max_length=50, unique=True, verbose_name=_("URL"), validators=[PUTKA_SLUG_VALIDATOR])
	set = models.ForeignKey('expurtka.Set', on_delete=models.PROTECT, blank=False, verbose_name=_("Set"), help_text=_("The set with tasks for this contest."))
	scheduled_start = models.DateTimeField(verbose_name=_("Start time"))
	duration_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Duration"), help_text=_("Duration of the contest in minutes."))
	autostart = models.BooleanField(default=False, verbose_name=_("Autostart"), help_text=_("Start the contest automatically at the specified time."))
	live_results = models.BooleanField(verbose_name=_("Live results"), help_text=_("Display current scoreboard to contestants during the contest."))
	auditable_results = models.BooleanField(default=False, verbose_name=_("Auditable results"), help_text=_("Show submissions to everyone after the contest."))
	public_testdata = models.BooleanField(default=False, verbose_name=_("Public test data"), help_text=_("Enable downloading test data zips after the contest."))
	scoring_type = models.IntegerField(choices=settings.CONTEST_SCORING_TYPES.choices, verbose_name=_("Scoring type"))
	freeze_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Freeze minutes"),
	                                             help_text=_("How many minutes before the end of the contest the scoreboard should freeze. Scoreboard-default behaviour if empty."))
	public = models.BooleanField(default=False, verbose_name=_("Public"))

	# These three fields define the state of the contest and only the following combinations of
	# values for (actual_start, actual_end, published) are valid:
	# UPCOMING: (null, null, False)
	# ONGOING: (time, null, False)
	# FINISHED: (time, time, False)
	# PUBLISHED: (time, time, True)
	actual_start = models.DateTimeField(null=True, blank=True)
	actual_end = models.DateTimeField(null=True, blank=True)
	published = models.BooleanField(default=False, verbose_name=_("Published"))

	contestants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='contests', through='Contestant', through_fields=('contest', 'user'))  # type: ignore[var-annotated]
	uploads = models.ManyToManyField('expurtka.Upload', related_name='contests', through='ContestUpload', through_fields=('contest', 'upload'))  # type: ignore[var-annotated]

	scoreboard = models.OneToOneField('StaticScoreboard', on_delete=models.SET_NULL, null=True, default=None, related_name='contest')

	user_perms = GenericRelation(UserObjectPermission)
	group_perms = GenericRelation(GroupObjectPermission)

	round_type: Optional[str]
	date: Optional[datetime.date]
	serverpush_skip_signal: bool

	class Meta(TypedModelMeta):
		ordering = ['scheduled_start', 'title']
		verbose_name = _('Contest')
		verbose_name_plural = _('Contests')

	objects = ContestQuerySet.as_manager()

	def __str__(self):
		return self.title

	@property
	def tasks(self):
		return self.set.tasks.order_by('links__sort')

	@property
	def duration(self):
		return datetime.timedelta(minutes=self.duration_minutes)

	def has_duration(self):
		return self.duration_minutes is not None

	def duration_humanize(self):
		hours = self.duration_minutes // 60
		minutes = self.duration_minutes % 60
		if hours > 0 and minutes > 0:
			return f"{hours}h {minutes}min"
		elif hours > 0:
			return f"{hours}h"
		else:
			return f"{minutes}min"

	def end_timestamp(self):
		"""Return Unix timestamp of contest end."""
		if not self.has_duration():
			return ''
		return str((self.actual_start + self.duration).timestamp())

	def time_until_str(self):
		if not self.has_duration():
			return ''

		remain = int((self.actual_start + self.duration - timezone.now()).total_seconds())
		if remain < 0:
			return '0:00:00'
		h, remain = divmod(remain, 3600)
		m, s = divmod(remain, 60)
		return f'{h:d}:{m:02d}:{s:02d}'

	def state(self) -> int:
		if self.actual_start is None:
			if self.actual_end is None and not self.published:
				return CONTEST_STATE.upcoming
			else:
				raise DataError(f"Contest object in an invalid state! (actual_start={self.actual_start}, "
				                f"actual_end={self.actual_end}, published={self.published})")
		else:
			if self.actual_end is None:
				if not self.published:
					return CONTEST_STATE.ongoing
				else:
					raise DataError(f"Contest object in an invalid state! (actual_start={self.actual_start}, "
					                f"actual_end={self.actual_end}, published={self.published})")
			else:
				if not self.published:
					return CONTEST_STATE.finished
				else:
					return CONTEST_STATE.published

	def is_upcoming(self):
		return self.state() == CONTEST_STATE.upcoming

	def is_ongoing(self):
		return self.state() == CONTEST_STATE.ongoing

	def is_finished(self):
		return self.state() == CONTEST_STATE.finished

	def is_published(self):
		return self.state() == CONTEST_STATE.published

	def is_active(self):
		return self.state() in [CONTEST_STATE.ongoing, CONTEST_STATE.finished]

	def is_over(self):
		return self.state() in [CONTEST_STATE.finished, CONTEST_STATE.published]

	def start(self):
		assert self.state() == CONTEST_STATE.upcoming, self.state()
		self.actual_start = timezone.now()

	def end(self):
		assert self.state() == CONTEST_STATE.ongoing, self.state()
		self.actual_end = timezone.now()

	def restart(self):
		assert self.state() == CONTEST_STATE.finished, self.state()
		self.actual_end = None

	def publish(self):
		assert self.state() == CONTEST_STATE.finished, self.state()
		self.published = True

	def unpublish(self):
		assert self.state() == CONTEST_STATE.published
		self.published = False

	def get_absolute_url(self):
		return reverse('contests:detail', args=(self.url,))


class Contestant(models.Model):
	contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	disqualified = models.BooleanField(default=False)

	class Meta(TypedModelMeta):
		constraints = [
			models.UniqueConstraint(fields=('contest', 'user'), name='%(app_label)s_%(class)s_unique'),
		]
		verbose_name = _('Contestant')
		verbose_name_plural = _('Contestants')


class ContestUpload(models.Model):
	contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
	upload = models.ForeignKey('expurtka.Upload', on_delete=models.CASCADE)
	disqualified = models.BooleanField(default=False)

	class Meta(TypedModelMeta):
		constraints = [
			models.UniqueConstraint(fields=('contest', 'upload'), name='%(app_label)s_%(class)s_unique'),
		]
		verbose_name = _('Contest upload')
		verbose_name_plural = _('Contest uploads')


class StaticScoreboard(models.Model):
	metadata = models.TextField()
	data = models.TextField()
	last_hint = models.TextField(null=True)

	class Meta(TypedModelMeta):
		verbose_name = _("Static scoreboard")
		verbose_name_plural = _("Static scoreboards")

	def marshal(self, **kwargs):
		"""Marshal the values given into json."""
		for k, v in kwargs.items():
			setattr(self, k, json.dumps(v, ensure_ascii=False))

	def unmarshal(self, *fields) -> tuple:
		"""Unmarshal the requested fields from json."""
		return tuple(json.loads(f) for f in fields)


class ContestGroup(models.Model):
	title = models.CharField(max_length=50, verbose_name=_("Title"))
	url = models.SlugField(max_length=50, unique=True, verbose_name=_("URL"), validators=[PUTKA_SLUG_VALIDATOR])

	rounds = models.ManyToManyField(Contest, related_name='contest_groups', through='ContestGroupMembership', through_fields=('group', 'contest'))  # type: ignore[var-annotated]

	scoring_type = models.IntegerField(choices=settings.CONTEST_GROUP_SCORING_TYPES.choices, verbose_name=_("Scoring type"))
	scoreboard = models.OneToOneField(StaticScoreboard, on_delete=models.SET_NULL, null=True, default=None, related_name='contest_group')

	class Meta(TypedModelMeta):
		ordering = ['title']
		verbose_name = _("Contest group")
		verbose_name_plural = _("Contest groups")

	def __str__(self):
		return self.title

	def has_scoring(self):
		return self.scoring_type != settings.CONTEST_GROUP_SCORING_TYPES.NONE


class ContestGroupMembership(models.Model):
	contest = models.ForeignKey(Contest, related_name='memberships', on_delete=models.CASCADE, verbose_name=_("Contest"))
	group = models.ForeignKey(ContestGroup, related_name='memberships', on_delete=models.CASCADE, verbose_name=_("Contest group"))
	round_type = models.IntegerField(choices=settings.CONTEST_ROUND_TYPES.choices, verbose_name=_("Round type"))

	class Meta(TypedModelMeta):
		constraints = [
			models.UniqueConstraint(fields=('contest', 'group'), name='%(app_label)s_%(class)s_unique'),
		]
		verbose_name = _("Contest round")
		verbose_name_plural = _("Contest rounds")

	def __str__(self):
		return f"Contest group membership (c={self.contest.url}, g={self.group.url})"
