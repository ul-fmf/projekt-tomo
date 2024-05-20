import re
from typing import TYPE_CHECKING, List

import expurtka.putka.config.settings as settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Case, Value, When
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django_stubs_ext.db.models import TypedModelMeta

if TYPE_CHECKING:
	from django.utils.functional import _StrOrPromise as StrOrPromise

HEADING_REGEX = re.compile(r'^(#{1,4} +.*) *$', re.MULTILINE)
# Both CRLF and LF need to be handled, because POST data sent by browsers can be encoded in both.
# See https://stackoverflow.com/questions/6963480/firefox-and-chrome-replacing-lf-with-crlf-during-post
# and https://code.djangoproject.com/ticket/19251.
SAMPLES_REGEX = re.compile(r'\r?\n\r?\n\{\{SAMPLES\}\}\r?\n\r?\n')


class ContentQuerySet(models.QuerySet):
	def lang_pref_order(self, pref_lang: str) -> 'ContentQuerySet':
		return self.alias(
			lang_pref=Case(When(lang=pref_lang, then=Value(1)), When(lang='en', then=Value(2)), default=3)
		).order_by('lang_pref', 'id')


class Content(models.Model):
	# Content type can be News or Task. These two also have GenericRelation to Content.
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	base_object = GenericForeignKey('content_type', 'object_id')

	lang = models.CharField(max_length=2, verbose_name=gettext_lazy('Language'))
	title = models.CharField(max_length=50, default=gettext_lazy('untitled'), verbose_name=gettext_lazy('Title'))
	content = models.TextField()
	# the following three fields should not be set directly, only implicitly by calling save()
	version = models.PositiveIntegerField(default=1)
	last_editor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
	last_edit_time = models.DateTimeField(auto_now=True)

	objects = ContentQuerySet.as_manager()

	class Meta(TypedModelMeta):
		verbose_name = gettext_lazy("Content")
		verbose_name_plural = gettext_lazy("Contents")

	def __str__(self):
		return f"{self.title} ({self.lang})"

	def save(self, update_fields=None, **kwargs):
		if 'editor' not in kwargs:
			raise ValueError("Argument `editor` missing when saving a Content instance.")
		self.version += 1
		self.last_editor = kwargs.pop('editor')
		if update_fields is not None:
			update_fields = {'last_editor', 'version'}.update(update_fields)
		super().save(**kwargs)

	def check_headings(self) -> List['StrOrPromise']:
		# Find what's missing in the content
		with translation.override(self.lang):
			headings_must = [
				'## ' + translation.gettext('Input data'),
				'## ' + translation.gettext('Output data')
			]
			headings_all = headings_must + [
				'## ' + translation.gettext('Task'),
				'### ' + translation.gettext('Input limits'),
				'### ' + translation.gettext('Comment')
			]

		headings_done = [h.strip() for h in HEADING_REGEX.findall(self.content)]
		warnings: List['StrOrPromise'] = []
		for h in set(headings_must) - set(headings_done):
			warnings.append(_('You should have a "%s" section!') % h)
		for h in set(headings_done) - set(headings_all):
			warnings.append(_('Unknown section heading: "%(heading)s". Try to use only these: %(options)s') % {
				'heading': h,
				'options': ', '.join(headings_all)
			})

		if not SAMPLES_REGEX.search(self.content):
			warnings.append(_(
				'Sample cases placeholder is missing. Add a {{SAMPLES}} tag surrounded by '
				'blank lines where you want the sample cases to appear.'
			))

		return warnings

	def get_absolute_url(self) -> str:
		if self.content_type == ContentType.objects.get_by_natural_key('core', 'task'):
			from expurtka.putka.models.tasks import Task
			assert isinstance(self.base_object, Task)
			return reverse('tasks:task-detail', args=(self.base_object.url, self.lang))
		if self.content_type == ContentType.objects.get_by_natural_key('news', 'news'):
			return reverse('news:landing')
		raise ValueError("Unknown Content content_type.")
