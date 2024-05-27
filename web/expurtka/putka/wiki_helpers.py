from typing import TYPE_CHECKING, Iterable, List, Optional, Union

import expurtka.putka.config.settings as settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    OuterRef,
    Prefetch,
    QuerySet,
    Subquery,
    prefetch_related_objects,
)
from expurtka.putka.models.wiki import Content, ContentQuerySet

if TYPE_CHECKING:
    from expurtka.putka.models.tasks import Task

    # from ui.news.models import News


def _get_best_content(
    content_list: Iterable[Content], preferred_lang: str
) -> Optional[Content]:
    """Return the content with the best language match given the preferences.

    Of the given content language variants `content_list`, return the one best matching
    language code `preferred_lang`. `content_list` must be an iterable of Content objects.
    """
    pref = None
    en = None
    first = None
    for content in content_list:
        if not pref and content.lang == preferred_lang:
            pref = content
        if not en and content.lang == "en":
            en = content
        if not first:
            first = content

    return pref or en or first or None


class ContentManagementMixin:
    """Mixin class for tasks and news for management of related content objects."""

    # Placeholders for related content objects.
    contents: List[Content]
    best_content_list: List[Content]
    best_content: Content
    best_title: str

    def fetch_contents(self, query=None, refresh_from_db=False):
        """Fetch related content objects from the database.

        This method is fine to be used on a single task, but is inefficient to use in a loop for multiple tasks.
        To fetch contents for multiple tasks use `annotate_tasks_with_contents`.
        """
        if (
            hasattr(self, "contents") and self.contents and not refresh_from_db
        ):  # Data has already been prefetched.
            return
        if query is None:
            query = self.content_queryset.only("lang", "title")
        self.contents = sorted(query, key=lambda c: settings.LANG_SORT_KEY[c.lang])

    def _find_best_content(self, pref_lang):
        best_content = _get_best_content(self.contents, pref_lang)
        assert (
            best_content is not None
        ), f"No contents found for object [{self.pk}]{self}"
        self.best_content = best_content

    def fetch_best_content(self, pref_lang, query=None):
        if hasattr(self, "contents"):
            self._find_best_content(pref_lang)
            return
        if query is None:
            query = self.content_queryset.only("lang", "title")
        self.best_content = query.lang_pref_order(pref_lang).first()

    @property
    def title(self):
        if hasattr(self, "best_title"):
            return self.best_title
        return self.best_content.title


# def annotate_objects_with_contents(objects: Iterable[Union['News', 'Task']], base_queryset: Optional[QuerySet[Content]] = None) -> None:
# 	"""Annotate a list of task objects with content metadata fetched from related content objects.

# 	The fetched related Content objects are stored in `contents` attribute of the task objects.

# 	Use `annotate_objects_with_best_content` or `with_best_title` if you only need the content with the best matching
# 	language or only the best matching title.
# 	"""
# 	if base_queryset is None:
# 		base_queryset = Content.objects.only('title', 'lang', 'object_id', 'content_type_id')

# 	prefetch_related_objects(objects, Prefetch('content_queryset', to_attr='contents', queryset=base_queryset))
# 	for obj in objects:
# 		obj.contents.sort(key=lambda c: settings.LANG_SORT_KEY[c.lang])


# def annotate_objects_with_best_content(objects: Iterable[Union['News', 'Task']], pref_lang: str, base_queryset: Optional[ContentQuerySet] = None) -> None:
# 	"""Annotate a list of task objects with best fitting content metadata fetched from related content objects.

# 	The fetched related Content object is stored in `best_content` attribute of the task objects.
# 	"""
# 	if base_queryset is None:
# 		base_queryset = Content.objects.only('title', 'lang', 'object_id', 'content_type_id')

# 	prefetch_related_objects(objects, Prefetch('content_queryset', to_attr='best_content_list', queryset=base_queryset.lang_pref_order(pref_lang)))
# 	for obj in objects:
# 		assert obj.best_content_list, f'No contents found for object [{obj.pk}]{obj}'
# 		obj.best_content = obj.best_content_list[0]


def best_title_subquery(pref_lang: str, id_field: str, model):
    """Return a subquery for fetching the best title.

    If possible, prefer to use the `with_best_title` method on the queryset.
    """
    return Subquery(
        Content.objects.filter(
            object_id=OuterRef(id_field),
            content_type=ContentType.objects.get_for_model(model),
        )
        .lang_pref_order(pref_lang)[:1]
        .values("title")
    )


class ContentQuerySetMixin:
    def with_best_title(self, pref_lang):
        return self.annotate(
            best_title=best_title_subquery(pref_lang, "id", self.model)
        )
