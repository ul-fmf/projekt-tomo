import hashlib
import os.path
import re
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Mapping, Optional, cast

import expurtka.putka.config.settings as settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import (
    Case,
    Count,
    Exists,
    F,
    FloatField,
    OuterRef,
    Prefetch,
    QuerySet,
    When,
    prefetch_related_objects,
)
from django.db.models.functions import Cast, Length
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta
from expurtka.putka.config.settings.enums import TASK_DIFFICULTY, TASK_EVALUATION_TYPES
# from ui.core.common.cache import cache_model_method_noarg
from expurtka.putka.slugify import PUTKA_SLUG_VALIDATOR
from expurtka.putka.models.contests import Contest
from expurtka.putka.pauth_helpers import PermissionQuerySetMixin
from expurtka.putka.models.pauth import GroupObjectPermission, UserObjectPermission
import expurtka.putka.results_helpers as results_helpers
from expurtka.putka.tasks_attachments import TEXT_TYPES, unixify_newlines
from expurtka.putka.wiki_helpers import (
    ContentManagementMixin,
    ContentQuerySetMixin,
    best_title_subquery,
)
from expurtka.putka.models.wiki import Content

if TYPE_CHECKING:
	from django.utils.functional import _StrOrPromise as StrOrPromise
	from expurtka.putka.models.results import Upload, UploadQuerySet


class Tag(models.Model):
	name = models.SlugField(
		max_length=50, verbose_name=_('Name'), unique=True, blank=False, null=False, validators=[PUTKA_SLUG_VALIDATOR],
		help_text=_('Tag name as displayed to the user. Separated with dashes and usually not capitalized. Currently not translatable.')
	)
	description = models.TextField(
		verbose_name=_('Description'), blank=False, null=False,
		help_text=_('Describe which type of tasks this tag represents. You can specify what tasks do and what tasks don\'t belong under this tag.')
	)

	class Meta(TypedModelMeta):
		verbose_name = _('Tag')
		verbose_name_plural = _('Tags')

	def __str__(self):
		return self.name


class TaskQuerySet(ContentQuerySetMixin, models.QuerySet):
	TASKS_SOLVED_Q = results_helpers.upload_solved_q_expr('upload__')

	def with_active_contests_info(self) -> 'TaskQuerySet':
		return self.annotate(in_active_contests=Exists(Contest.objects.ongoing().filter(set__tasks=OuterRef('pk'))))

	def with_is_solved(self, user) -> 'TaskQuerySet':
		return self.annotate(is_solved=Exists(user.upload_set.solved().filter(task_id=OuterRef('pk'))))

	def with_success_ratio(self) -> 'TaskQuerySet':
		return (
			self
			.annotate(submitter_count=Count('upload__user', distinct=True))
			.annotate(submitter_count_ok=Count('upload__user', filter=self.TASKS_SOLVED_Q, distinct=True))
			.annotate(submitter_count_float=Cast('submitter_count', output_field=FloatField()))
			.annotate(submitter_count_ok_float=Cast('submitter_count_ok', output_field=FloatField()))
			.annotate(success_ratio=Case(
				When(submitter_count_float=0, then=None),
				default=F('submitter_count_ok_float') / F('submitter_count_float')
			))
		)


# Authors are strings, which can be just "John Doe", or "John Doe (Contest 2022)".
# This regex finds the portion in the parenthesis, if present.
_SOURCE_REGEX = re.compile(r'\(.*?\)')
_TIME_LIMIT_REGEX = re.compile(r'jail\.limits\.time\s*=\s*(.+)')
_MEMORY_LIMIT_REGEX = re.compile(r'jail\.limits\.memory\s*=\s*(.+)')
_SUBTASKS_REGEX = re.compile(r'(?:SUBTASKS\s*=|putka\.agg\.subtasked\()\s*\[\s*((?:\d+\s*,?\s*)+)]')


class Task(ContentManagementMixin, models.Model):
	url = models.SlugField(
		max_length=50, unique=True, verbose_name=_('URL'), validators=[PUTKA_SLUG_VALIDATOR],
		help_text=_('Preferably contains letters, numbers and dashes, but can be any slug. It must be globally unique.')
	)
	author = models.CharField(
		max_length=50, null=True, blank=True, verbose_name=_('Author'),
		help_text=_('The "Author (Contest)" syntax may be used to specify the task source or the original contest it appeared in.'),
	)
	evaluation_type = models.PositiveSmallIntegerField(
		choices=TASK_EVALUATION_TYPES.choices, verbose_name=_('Evaluation type'),
		help_text=_('Determines how the submitted solution will be evaluated.')
	)
	difficulty = models.PositiveSmallIntegerField(
		null=True, blank=True, default=None,
		choices=TASK_DIFFICULTY.choices + [(None, _('Unspecified'))],
		verbose_name=_('Difficulty'), help_text=_('Estimated task difficulty as intended by the author.'),
	)
	tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("Tags"), help_text=_("Add all applicable tags. Always try to add at least one tag. You can create a new one, if really needed."))
	testscript = models.TextField(null=False)
	parents = models.ManyToManyField(to='expurtka.Set', through='expurtka.TaskLink', related_name='tasks')

	content_queryset = GenericRelation(Content)

	objects = TaskQuerySet.as_manager()

	tag_list: List[Tag]
	parent_list: List['Set']
	in_active_contests: bool
	link: 'TaskLink'
	selected_upload: Optional['Upload']

	class Meta(TypedModelMeta):
		verbose_name = _("Task")
		verbose_name_plural = _("Tasks")

	def __repr__(self):
		return f"Task(url='{self.url}', id={self.id})"

	def __str__(self):
		return f"{self.url} ({self.id})"

	def get_absolute_url(self, lang: Optional[str] = None) -> str:
		if lang is None:
			return reverse('tasks:task-detail', args=(self.url,))
		return reverse('tasks:task-detail', args=(self.url, lang))

	def author_no_source(self) -> str:
		return _SOURCE_REGEX.sub('', self.author or '?').strip() or '?'

	def source(self) -> Optional[str]:
		source = _SOURCE_REGEX.search(self.author or '?')
		return source.group(0)[1:-1].strip() if source else None

	def difficulty_description(self) -> Optional[str]:
		return settings.TASK_DIFFICULTY(self.difficulty).label if self.difficulty else None

	def attachments(self):
		"""Return a queryset of all attachments, excluding sample test data."""
		return self.file_set.exclude(type=settings.ATT_TYPE.inout_public).order_by('filename')

	def attachments_by_type(self, att_type=None):
		q = self.attachments()
		if att_type is not None:
			q = q.filter(type=att_type)
		return q

	def samples(self) -> QuerySet['File']:
		return self.file_set.filter(type=settings.ATT_TYPE.inout_public).order_by('filename')

	def sample_pairs(self):
		"""Return the associated public in/out File objects structured into a list of pairs [(input, output),...].

		If a file does not have a matching pair, the missing file is represented with None.
		The returned list is sorted by filename.
		"""
		pairs = defaultdict(lambda: [None, None])
		for sample in self.sample_list:  # Sample list prefetched when getting the task.
			base, ext = os.path.splitext(sample.filename)
			pairs[base][0 if ext == ".pubin" else 1] = sample
		return list(pairs.values())

	def get_limits(self) -> Dict[str, float]:
		"""Obtain limits (mem, cpu, ...) heuristically.

		This parses the test script and observes the defaults. The limits are returned
		as a dict. See source code for dict keys.
		"""
		from expurtka.putka.helpers import (
		    eval_arithmetic,  # avoid load-time circular dependencies
		)

		# initialize with defaults (TODO?: these are hardcoded both here and in tester/test.cpp; move to common config)
		time = 2.0
		mem = 32
		# try to parse the test script
		if m := _TIME_LIMIT_REGEX.search(self.testscript):
			time = eval_arithmetic(m.group(1)) or time
		if m := _MEMORY_LIMIT_REGEX.search(self.testscript):
			mem = eval_arithmetic(m.group(1)) or mem

		return {'memory': mem, 'time': time}

	# XXX: hack, the backend should likely populate the TestCase models with subtask information as determined
	# by the testscript.
	def subtask_info(self) -> Optional[List[int]]:
		"""Return a list of points per subtask, if detected in the testscript."""
		subtask_str = _SUBTASKS_REGEX.search(self.testscript)
		if not subtask_str:
			return None
		try:
			subtasks = [int(x) for x in subtask_str.group(1).split(',') if x.strip()]
		except ValueError:
			return None
		return subtasks or None

	def official_solutions(self) -> 'UploadQuerySet':
		"""Return a queryset of uploads marked as official solutions."""
		return self.upload_set.filter(is_official_solution=True)

	def sample_validity(self) -> Mapping[str, int]:
		"""Return a dict mapping each sample case to its validity.

		The validity is computed based on the aggregate of the results of official solutions on each sample.

		The returned dict is empty if there are no official solutions.
		"""
		from expurtka.putka.models.results import TestCase
		sample_testcases = TestCase.objects.filter(name__endswith='.pubin', upload__task_id=self.id, upload__is_official_solution=True).order_by().only('run_status', 'points', 'max_points', 'upload_id', 'name')
		sample_statuses = defaultdict(list)
		for test in sample_testcases:
			sample_statuses[cast(str, test.name)].append(test.status())

		sample_validity = {}
		for case in sample_statuses:
			statuses = sample_statuses[case]
			if any(s is None for s in statuses):
				sample_validity[case] = settings.SAMPLE_VALIDITY.undetermined
			elif all(s == settings.JAILRUN_STATUS.OK for s in statuses):
				sample_validity[case] = settings.SAMPLE_VALIDITY.ok
			elif all(s != settings.JAILRUN_STATUS.OK for s in statuses):
				sample_validity[case] = settings.SAMPLE_VALIDITY.fail
			else:
				sample_validity[case] = settings.SAMPLE_VALIDITY.mixed
		return sample_validity

	def has_server_evaluation(self):
		return self.evaluation_type == settings.TASK_EVALUATION_TYPES.server_evaluation

	def has_local_evaluation(self):
		return self.evaluation_type == settings.TASK_EVALUATION_TYPES.local_evaluation

	def has_manual_evaluation(self):
		return self.evaluation_type == settings.TASK_EVALUATION_TYPES.manual_evaluation


class SetQuerySet(PermissionQuerySetMixin, models.QuerySet):
	pass


class Set(models.Model):
	parent = models.ForeignKey('self', null=True, on_delete=models.PROTECT, related_name='child_sets', verbose_name=_("Parent"))
	title = models.CharField(max_length=50, verbose_name=_("Title"))
	url = models.SlugField(
		max_length=50, verbose_name=_("URL"), validators=[PUTKA_SLUG_VALIDATOR],
		help_text=_("Url of this set. Must be unique within the parent set.")
	)
	description = models.TextField(null=True, blank=True, verbose_name=_("Description"), help_text=_("You can use Markdown such as *...* or `...` and LaTeX with $...$.'"))
	public = models.BooleanField(default=False, verbose_name=_("Public"), help_text=_("This set will be visible to all users, even if not logged in."))
	sort = models.PositiveIntegerField()

	user_perms = GenericRelation(UserObjectPermission)
	group_perms = GenericRelation(GroupObjectPermission)

	_root: 'Set'

	objects = SetQuerySet.as_manager()

	class Meta(TypedModelMeta):
		verbose_name = _("Set")
		verbose_name_plural = _("Sets")

	def __str__(self):
		return self.display_title()

	def display_title(self) -> 'StrOrPromise':
		if self == Set.root():
			return gettext("Tasks")
		return self.title

	def __repr__(self):
		return f"Set(title='{self.title}', url='{self.url}', id={self.id})"

	@classmethod
	def root(cls) -> 'Set':
		if hasattr(cls, '_root'):
			return cls._root
		try:
			# Both of the properties below must hold for the root element, and either of them identifies it uniquely.
			cls._root = cls.objects.get(url='', parent__isnull=True)
			return cls._root
		except Set.DoesNotExist:
			raise ImproperlyConfigured(
				"A root Set with empty url and null parent must be present in the database for putka to function. "
				"Did you run 'putkainit' before starting?"
			)

	# @cache_model_method_noarg(group="set_paths")
	# def absolute_path(self) -> str:
	# 	"""Return the absolute path of this set, e.g. /a/b/c/."""
	# 	if self.parent is None:
	# 		return '/'
	# 	return self.parent.absolute_path() + self.url + '/'

	# @cache_model_method_noarg(group="set_paths")
	# def root_path(self) -> List['Set']:
	# 	if self.parent is None:
	# 		return [self]
	# 	return self.parent.root_path() + [self]

	def subset_ids(self, r=None) -> List[int]:
		"""Return a list of all subset id-s as obtained by a preorder tree traversal."""
		prefetch = Prefetch('child_sets', to_attr='child_set_list')
		if r is None:
			r = []
			# Prefetching saves the lowest level of queries.
			child_sets = self.child_sets.prefetch_related(prefetch)
		else:
			# TODO: https://github.com/typeddjango/django-stubs/issues/795
			child_sets = self.child_set_list  # type:ignore[attr-defined]
			prefetch_related_objects(child_sets, prefetch)

		r.append(self.id)
		for s in child_sets:
			s.subset_ids(r)
		return r

	def get_absolute_url(self) -> str:
		return reverse('tasks:set-detail', args=(self.absolute_path(),))

	def tasks_with_links_and_titles(self, pref_lang) -> List[Task]:
		"""Return a dict of tasks in this set in the correct order, keyed by task_id."""
		query = self.links.order_by('sort').select_related('task').annotate(best_title=best_title_subquery(pref_lang, 'task_id', Task))
		links = {link.task_id: link for link in query}
		tasks = [link.task for link in links.values()]
		for task in tasks:
			task.link = links[task.id]
			task.best_title = task.link.best_title
		return tasks


class TaskLink(models.Model):
	"""Soft link connecting a task to a set."""

	parent = models.ForeignKey(Set, related_name='links', on_delete=models.CASCADE)
	task = models.ForeignKey(Task, related_name='links', on_delete=models.CASCADE)
	sort = models.PositiveIntegerField(null=False)

	matched_contents: List[Content]

	class Meta(TypedModelMeta):
		constraints = [
			models.UniqueConstraint(fields=('parent', 'task'), name='%(app_label)s_%(class)s_unique'),
		]

	def __repr__(self):
		return f"TaskLink(id={self.id}, parent={self.parent}, task={self.task_id}, sort={self.sort})"


class FileQuerySet(models.QuerySet):
	def inputs_and_outputs(self) -> 'FileQuerySet':
		return self.filter(type__in=(settings.ATT_TYPE.inout_public, settings.ATT_TYPE.inout_secret))

	def only_data_size(self) -> 'FileQuerySet':
		return self.annotate(data_size=Length('data'))

	def private(self) -> 'FileQuerySet':
		return self.filter(type__lt=0)


class FileManager(models.Manager):
	def get_queryset(self) -> FileQuerySet:
		# This is almost always correct and is almost always a significant performance improvement
		# since most of the ui doesn't show file contents. But it does introduce a data corruption
		# if not used carefully; accessing a deferred field causes a refresh_from_db, which will
		# overwrite any dirty fields the object may have. In particular, take care with update views.
		return FileQuerySet(self.model, using=self._db).defer('data')


class File(models.Model):
	task = models.ForeignKey(Task, verbose_name=_("Task"), on_delete=models.CASCADE)
	filename = models.CharField(verbose_name=_("Filename"), max_length=50)
	type = models.IntegerField(verbose_name=_("Attachment type"), null=False, choices=settings.ATT_TYPE.choices, default=None)
	data = models.BinaryField(verbose_name=_("Data"), null=False)
	md5 = models.CharField(verbose_name=_("MD5 hash"), max_length=32, null=False, default='deadbeef')  # should not be set manually; computed from data automatically on each save()

	objects = FileManager.from_queryset(FileQuerySet)()

	class Meta(TypedModelMeta):
		unique_together = ('task', 'filename')
		verbose_name = _("File")
		verbose_name_plural = _("Files")
		base_manager_name = 'objects'

	def __str__(self):
		return self.filename

	def clean(self):
		if self.type in TEXT_TYPES:
			nice_data = unixify_newlines(bytes(self.data))
			if self.data != nice_data:
				self.data = nice_data
				self.cleaned_newlines = True
				return
		self.cleaned_newlines = False

	def compute_md5(self):
		self.md5 = hashlib.md5(self.data).hexdigest()

	def save(self, *args, update_fields=None, **kwargs):
		if self.type == settings.ATT_TYPE.inout_public and not (self.filename.endswith('.pubin') or self.filename.endswith('.pubout')):
			raise ValueError("A file of type inout_public must have extension .pubin or .pubout; got %s." % repr(self.filename))
		if self.type == settings.ATT_TYPE.inout_secret and not (self.filename.endswith('.in') or self.filename.endswith('.out')):
			raise ValueError("A file of type inout_secret must have extension .in or .out; got %s." % repr(self.filename))
		self.compute_md5()
		if update_fields is not None:
			update_fields = {'md5'}.update(update_fields)
		super().save(*args, update_fields=update_fields, **kwargs)
