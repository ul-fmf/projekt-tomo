from functools import cache

from django_stubs_ext.db.models import TypedModelMeta

import expurtka.putka.config.settings as settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from expurtka.putka.config.settings.enums import THREAD_TYPES
from expurtka.putka.models.alerts import Alert
from expurtka.putka.slugify import PUTKA_SLUG_VALIDATOR
from expurtka.putka.models.contests import Contest
from expurtka.putka.models.pauth import GroupObjectPermission, UserObjectPermission
# from ui.core.pauth.permissions import all_with_explicit_perm
from expurtka.putka.models.tasks import Set


class Forum(models.Model):
	title = models.CharField(max_length=50, verbose_name=_('Title'))
	description = models.TextField(verbose_name=_('Description'))
	url = models.SlugField(max_length=50, unique=True, verbose_name=_('URL'), validators=[PUTKA_SLUG_VALIDATOR])

	def __str__(self):
		return f"{self.title} (/{self.url}/)"


@cache
def thread_content_types() -> list[int]:
	"""Return an iterable of all thread-related content type ids."""
	return list(map(lambda c: ContentType.objects.get_for_model(c).id, (GeneralThread, TaskThread, ContestThread)))


class Thread(models.Model):
	"""Base class for forum threads."""

	date_created = models.DateTimeField(auto_now_add=True)
	thread_type = models.SlugField(max_length=1, choices=settings.THREAD_TYPES.choices, editable=False)

	# GenericRelation must be present to support cascading deletion of alerts when a post is deleted.
	alerts = GenericRelation(Alert)

	class Meta(TypedModelMeta):
		ordering = ['-date_created']

	def __repr__(self):
		c = self.concrete()
		return f"Thread(parent_id={self.id}, id={c.id}, uid={c.uid()}, type={c.type()})"

	def __str__(self):
		c = self.concrete()
		return f"Thread '{c.uid()}' ({c.type()})"

	def concrete(self) -> 'Thread':
		"""Return the properly typed instance of this thread."""
		if isinstance(self, Thread) and type(self) is not Thread:
			return self

		if self.thread_type == settings.THREAD_TYPES.general:
			return self.generalthread
		elif self.thread_type == settings.THREAD_TYPES.task:
			return self.taskthread
		elif self.thread_type == settings.THREAD_TYPES.contest:
			return self.contestthread
		else:
			raise TypeError(f"Thread {self.pk} is not convertible to a concrete child class.")

	def forum_url(self) -> str:
		"""Return forum url for this thread.

		This is an actual forum url in case of general threads, and an URL placeholder for other types.
		"""
		raise NotImplementedError

	def uid(self) -> str:
		"""Return a human readable unique identifier for this thread."""
		raise NotImplementedError

	@staticmethod
	def type() -> int:
		"""Return the type of the current thread."""
		raise NotImplementedError

	def best_title(self, lang) -> str:
		"""Return title of this thread, preferably in the given language."""
		raise NotImplementedError


class GeneralThread(Thread):
	"""General conversation thread."""

	MAX_TITLE_LENGTH = 50

	title = models.CharField(max_length=MAX_TITLE_LENGTH, verbose_name=_('Title'))
	url = models.SlugField(unique=True, verbose_name=_('URL'), validators=[PUTKA_SLUG_VALIDATOR])
	forum = models.ForeignKey(Forum, related_name='threads', on_delete=models.CASCADE, verbose_name=_('Forum'))
	closed = models.BooleanField(default=False, verbose_name=_('Closed'), help_text=_('Closed threads do not allow adding new posts.'))

	def __init__(self, *args, **kwargs):
		if not args:
			kwargs['thread_type'] = settings.THREAD_TYPES.general
		super().__init__(*args, **kwargs)

	def forum_url(self):
		return self.forum.url

	def uid(self):
		return self.url

	@staticmethod
	def type():
		return THREAD_TYPES.general

	def best_title(self, lang):
		return self.title


class TaskThread(Thread):
	"""Thread associated with a task."""

	task = models.OneToOneField('expurtka.Task', related_name='thread', on_delete=models.CASCADE)

	def __init__(self, *args, **kwargs):
		if not args:
			kwargs['thread_type'] = settings.THREAD_TYPES.task
		super().__init__(*args, **kwargs)

	def forum_url(self):
		return 'tasks'

	def uid(self):
		return self.task.url

	@staticmethod
	def type():
		return THREAD_TYPES.task

	def best_title(self, lang):
		self.task.fetch_best_content(lang)
		return self.task.title


class ContestThread(Thread):
	"""Thread associated with a contest."""

	contest = models.OneToOneField(Contest, related_name='thread', on_delete=models.CASCADE)

	def __init__(self, *args, **kwargs):
		if not args:
			kwargs['thread_type'] = settings.THREAD_TYPES.contest
		super().__init__(*args, **kwargs)

	def forum_url(self):
		return 'contests'

	def uid(self):
		return self.contest.url

	@staticmethod
	def type():
		return THREAD_TYPES.contest

	def best_title(self, lang):
		return self.contest.title


class Post(models.Model):
	thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	content = models.TextField()
	date_posted = models.DateTimeField(auto_now_add=True)
	public = models.BooleanField(null=False)
	# the following three fields should not be set directly, only implicitly by calling save()
	version = models.PositiveIntegerField(default=1)
	last_editor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='posts_edited_set', on_delete=models.SET_NULL)
	last_edit_time = models.DateTimeField(auto_now=True)

	user_perms = GenericRelation(UserObjectPermission)
	group_perms = GenericRelation(GroupObjectPermission)

	class Meta(TypedModelMeta):
		ordering = ['date_posted']

	def __str__(self):
		return f"Post(id={self.id}, content='{self.content[:10]}...')"

	# def _interested_users(self):
	# 	"""Construct a QuerySet of users who want to receive notifications about this post."""
	# 	User = get_user_model()
	# 	FN = settings.FORUM_NOTIFY
	# 	recently = timezone.now() - settings.FORUM_RECENT_SPAN

	# 	admins = User.objects.filter(
	# 		is_superuser=True,
	# 		is_active=True,
	# 		profile__forum_notify__gt=FN.never
	# 	)

	# 	# Explicit addressees; try notifying all users with view permissions on this post,
	# 	# regardless of any of the recency checks below.
	# 	if not self.public:
	# 		return (
	# 			User.objects
	# 			.exclude(profile__forum_notify=FN.never)
	# 			.exclude(is_active=False)
	# 			.intersection(
	# 				all_with_explicit_perm(obj=self),
	# 			)
	# 			.union(admins)
	# 		)

	# 	# If the post is public, notify people who might be interested:

	# 	# People who recently wrote in the thread.
	# 	recent_authors = User.objects.filter(post__date_posted__gte=recently, post__thread=self.thread)

	# 	# People who recently attempted this thread's task or just partook in a contest containing this thread's task.
	# 	try:
	# 		recent_solvers_task = User.objects.filter(
	# 			upload__task=self.thread.taskthread.task,
	# 			upload__upload_time__gte=recently,
	# 		)

	# 		actual_task_sets = Set.objects.filter(tasks=self.thread.taskthread.task)

	# 		recent_contests = Contest.objects.filter(
	# 			set__in=actual_task_sets,
	# 			actual_start__gte=recently,
	# 		)
	# 		recent_solvers_contests = User.objects.filter(
	# 			contests__in=recent_contests,
	# 		)
	# 	except TaskThread.DoesNotExist:
	# 		# No task associated with the thread.
	# 		recent_solvers_task = User.objects.none()
	# 		recent_solvers_contests = User.objects.none()

	# 	# People who participated in a contest that the thread relates to.
	# 	try:
	# 		contestants = User.objects.filter(
	# 			contests=self.thread.contestthread.contest,
	# 			contests__actual_start__gte=recently,
	# 		)
	# 	except ContestThread.DoesNotExist:
	# 		# No contest associated with the thread.
	# 		contestants = User.objects.none()

	# 	recent_active = User.objects.filter(profile__forum_notify__gte=FN.recent_active)
	# 	recent_passive = User.objects.filter(profile__forum_notify__gte=FN.recent_passive)

	# 	return (
	# 		User.objects.none().union(
	# 			User.objects.filter(profile__forum_notify__gte=FN.always),
	# 			recent_authors.intersection(recent_active),
	# 			recent_solvers_task.intersection(recent_passive),
	# 			recent_solvers_contests.intersection(recent_passive),
	# 			contestants,
	# 		)
	# 		.intersection(
	# 			User.objects.filter(is_active=True),
	# 		)
	# 	)

	def create_alerts(self):
		# Create notifications for interested users.
		listeners = self._interested_users()
		alerts = []
		for u in listeners:
			if u == self.last_editor:
				continue
			alerts.append(Alert.for_thread_activity(user=u, thread=self.thread.concrete()))
		Alert.objects.bulk_create(alerts, ignore_conflicts=True)
		Alert.ajax_wake()

	def save(self, update_fields=None, **kwargs):
		if 'editor' not in kwargs:
			raise ValueError("Argument `editor` missing when saving a Post instance.")
		# update version and last editor
		editor = kwargs.pop('editor')
		self.last_editor = editor
		self.version += 1
		if update_fields is not None:
			update_fields = {'last_editor', 'version'}.update(update_fields)
		super().save(update_fields=update_fields, **kwargs)
