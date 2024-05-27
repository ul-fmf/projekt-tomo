import asyncio
import importlib
import json
import logging
import os
import random
import re
from dataclasses import dataclass
from functools import cached_property
from typing import IO, TYPE_CHECKING, Callable, Protocol

import expurtka.putka.config.settings as settings
import ipwhois
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.core.files.uploadhandler import StopUpload, TemporaryFileUploadHandler
from django.core.paginator import Page, Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    JsonResponse,
    StreamingHttpResponse,
)
from django.template.response import SimpleTemplateResponse
from django.utils import translation
from django.utils.functional import Promise, lazy

if TYPE_CHECKING:
    from django.utils.functional import _StrOrPromise as StrOrPromise
    from expurtka.putka.models.users import User

logger = logging.getLogger(__name__)  # noqa


class AuthenticatedHttpRequest(HttpRequest):
    """Request class for typing purposes.

    https://github.com/typeddjango/django-stubs#how-can-i-create-a-httprequest-thats-guaranteed-to-have-an-authenticated-user
    """

    user: "User"


@dataclass(slots=True, frozen=True)
class Breadcrumb:
    """A single breadcrumb item for the top bar."""

    url: str
    title: "StrOrPromise"


def get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def create_password(length=8):
    """Create a random password of given length with easily distinguishable characters."""
    chars = "abcdefghijkmnpqrstyABCDEFGHJKLMNPQRSTY23456789#%&*[]()"
    return "".join(random.choice(chars) for _ in range(length))


def identifier_form(txt):
    """Compress `txt` into a form suitable for an indetifier: allow only [a-zA-Z0-9_] in the result.

    Takes special care of slovene characters (->csz). Spaces are reflected in camelCase.
    """
    # replace slovene chars
    # convert whitespace to camelCase, strip forbidden chars
    txt = csz(txt).lower()
    txt = re.sub("[^a-zA-Z0-9_]+([a-zA-Z]?)", lambda m: m.group(1).upper(), txt)
    return txt


def csz(txt):
    """Replace slovene characters in text with csz."""
    for slo, ascii in zip("čšžćđČŠŽĆĐ", "cszcdCSZCD"):
        txt = txt.replace(slo, ascii)
    return txt


def preferred_lang(user):
    profile_lang = user.profile.lang if user.is_authenticated else None
    return profile_lang or translation.get_language()


def eval_arithmetic(txt):
    """Compute the value of a given simple expression.

    If txt is a valid simple arithmetic expression involving only constants, returns its value.
    Otherwise, returns None.
    """
    # strip comments
    txt = txt.split("#")[0].strip()
    if not re.match(r"[\s0-9\+\-\*\.\(\)%\^\|/]+", txt):
        return None
    try:
        return eval(txt, {}, {})
    except:
        return None


def call_with_async_pipe(func: Callable[..., None], *args, **kwargs) -> IO[bytes]:
    """Speed up processing of data streams by executing writes asynchronously.

    Execute `func` asynchronously and pass it the write end of a pipe as first
    argument. Return the read end of that pipe and enable caller to consume
    what `func` has written before writing is complete.

    Caller is responsible for closing the read end and `func` is responsible
    for closing the write end.
    """
    read_fd, write_fd = os.pipe()

    def _wrapped_func():
        handle = os.fdopen(write_fd, "wb")
        try:
            func(handle, *args, **kwargs)
        except BrokenPipeError:
            pass
        except:
            logger.exception("call_with_async_pipe function crashed")
        finally:
            try:
                handle.close()
            except BrokenPipeError:
                pass

    async def _thunk():
        asyncio.ensure_future(
            database_sync_to_async(_wrapped_func, thread_sensitive=False)()
        )

    async_to_sync(_thunk)()
    return os.fdopen(read_fd, "rb")


class ClassPath(str):
    """Shortcut string wrapper for getting module attributes by path.

    For example, ClassPath('ui.core.common.helpers.ClassPath')() will return
    the ClassPath class object.
    """

    def __call__(self):
        # module_name, _, class_name = self.rpartition('.')
        # module = importlib.import_module(module_name)
        # return getattr(module, class_name)
        pass


class IPMeta:
    """Metadata object for whois records about a given ip."""

    TIMEOUT = 3600 * 24 * 180  # about half a year, in seconds

    def __init__(self, ip):
        if not isinstance(ip, str):
            ip = get_request_ip(ip)
        self.ip = ip
        self.cache_key = f"ipwhois-{self.ip}"
        self.dummy = False
        cached = cache.get(self.cache_key)
        if cached is None:
            try:
                cached = ipwhois.IPWhois(self.ip).lookup_rdap()
            except:
                cached = {
                    "_dummy": True,
                    "asn_country_code": "##",
                    "asn_description": "<unknown asn>",
                    "network": {
                        "name": "<unknown network>",
                    },
                }
            cache.set(self.cache_key, cached, timeout=self.TIMEOUT)
        else:
            cache.touch(self.cache_key, timeout=self.TIMEOUT)
        self.data = cached
        self.dummy = self.data.get("_dummy", False)
        self.country = self.data.get("asn_country_code", "##")
        self.description = self.data.get("asn_description", "<unknown asn>")
        self.network = self.data.get("network", {}).get("name", "<unknown network>")

    def __str__(self):
        return f"{self.description} / {self.network}"

    def check_country(self, countries=None) -> bool:
        """Check if the IP is likely from an acceptable country."""
        if countries is None:
            countries = settings.REGISTRATION_COUNTRIES
        return self.dummy or not countries or self.country in countries


def get_request_ip(request: HttpRequest) -> str:
    """Return the remote client IP that made the given request."""
    ip_list = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR"))
    return ip_list.split(", ")[0]


class JSONProxyEncoder(DjangoJSONEncoder):
    """JSON encoder wrapper for Django-style lazy functions."""

    def default(self, o):
        if isinstance(o, Promise):
            # Promise is Django's marker class for lazy evaluation wrappers. On creation,
            # the wrapper inspects the wrapped function's return value type and copies
            # wrapped variants of all its methods into itself, so we can't really hook into
            # any of those at runtime - the wrapper always only evaluates the function just before
            # calling the wrapped method, so the result isn't cached anywhere. However, for comparison
            # operators, if the right hand operand is also a Promise, its internal downcast function
            # will be called on it before handing control over to the wrappee's (i.e. left operand's)
            # operator... so we need to be the left hand side in a comparison expression in order to get
            # the unwrapped evaluated result of the lazy function. This gives us a downcast right operand,
            # which we can sleazily return as the comparison's result, furnishing us with the
            # evaluated lazy without having to resort to unstably using the actual functions
            # (the downcast is implemented as o._proxy____cast()).
            class __Incomparable__:
                def __lt__(self, other):
                    return other

            # Make `incomparable` be a lazy-evaluated ctor for `__Incomparable__`.
            # `incomparable()` is therefore a Promise, so comparisons will go through the proxy
            # implementation's wrappers... which will neatly downcast the right operand, because it
            # is also a Promise, and give the result to us.
            incomparable = lazy(__Incomparable__, __Incomparable__)
            return incomparable() < o
        return super().default(o)


def json_dumps(obj, cls=JSONProxyEncoder, **kwargs):
    return json.dumps(obj, ensure_ascii=False, cls=cls, **kwargs)


class StructuredJsonResponse(JsonResponse):
    """A more structured JsonResponse meant for ajax form submission."""

    REDIRECT = "redirect"
    REFRESH = "refresh"
    SUCCESS = "success"
    DISPLAY = "display"
    ACTIONS = (REDIRECT, DISPLAY, REFRESH, SUCCESS)

    def __init__(self, *, action, payload, **kwargs):
        assert action in self.ACTIONS, f"Action {action} is not one of {self.ACTIONS}"
        super().__init__(
            {"action": action, "payload": payload}, JSONProxyEncoder, **kwargs
        )

    @staticmethod
    def refresh():
        return StructuredJsonResponse(
            action=StructuredJsonResponse.REFRESH, payload=None
        )

    @staticmethod
    def redirect(url):
        return StructuredJsonResponse(
            action=StructuredJsonResponse.REDIRECT, payload=url
        )

    @staticmethod
    def success():
        return StructuredJsonResponse(
            action=StructuredJsonResponse.SUCCESS, payload=None
        )

    @staticmethod
    def display(content):
        return StructuredJsonResponse(
            action=StructuredJsonResponse.DISPLAY, payload=content
        )


class FormViewClassProtocol(Protocol):
    """Mixin typing helper."""

    def get_success_url(self) -> str:
        ...

    def form_valid(self, form) -> HttpResponse:
        ...


class TemplateViewClassProtocol(Protocol):
    """Mixin typing helper."""

    def render_to_response(self, context, **response_kwargs) -> SimpleTemplateResponse:
        ...


class SingleObjectView(Protocol):
    """Mixin typing helper."""

    request: HttpRequest

    def get_object(self) -> Model:
        ...


class FileLike(Protocol):
    """Export typing helper."""

    filename: str
    data: bytes


class JsonResponseMixin:
    """Mixin that returns StructuredJsonResponse.

    It is intended to be used with generic CreateView, UpdateView and DeleteView classes,
    which are called using ajax and are expected to return StructuredJsonResponses.
    """

    def form_valid(self: FormViewClassProtocol, form) -> HttpResponse:
        super().form_valid(form)  # type:ignore[safe-super]
        return StructuredJsonResponse.redirect(self.get_success_url())

    def render_to_response(
        self: TemplateViewClassProtocol, context, **response_kwargs
    ) -> HttpResponse:
        response = super().render_to_response(
            context, **response_kwargs
        )  # type:ignore[safe-super]
        if response.status_code == 200:
            return StructuredJsonResponse.display(response.rendered_content)
        else:
            return response


class log_and_ignore_exceptions:
    """Catch all exceptions in either the context or the decorated callable.

    The exceptions are logged but otherwise suppressed.
    """

    def __init__(self, name, message):
        self.name = name
        self.message = message

    def __call__(self, func):
        # Used as a decorator.
        if asyncio.iscoroutinefunction(func) or hasattr(func, "__acall__"):

            async def _wrap(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except asyncio.CancelledError:
                    pass
                except:
                    logging.getLogger(self.name).exception(self.message)
                    # Return None.

        else:

            def _wrap(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except asyncio.CancelledError:
                    pass
                except:
                    logging.getLogger(self.name).exception(self.message)
                    # Return None.

        return _wrap

    def __enter__(self):
        # Used as a context manager.
        return self

    def __exit__(self, typ, val, tb):
        if val is not None and typ is not asyncio.CancelledError:
            logging.getLogger(self.name).exception(self.message)
        return True


class LimitedTemporaryFileUploadHandler(TemporaryFileUploadHandler):
    def __init__(self, size_limit, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._size_limit = size_limit
        self._size_so_far = 0

    def new_file(
        self,
        field_name,
        file_name,
        content_type,
        content_length,
        charset=None,
        content_type_extra=None,
    ):
        if content_length is not None and content_length > self._size_limit:
            raise StopUpload(connection_reset=True)
        self._size_so_far = 0
        return super().new_file(
            field_name,
            file_name,
            content_type,
            content_length,
            charset=charset,
            content_type_extra=content_type_extra,
        )

    def receive_data_chunk(self, raw_data, start):
        self._size_so_far += len(raw_data)
        if self._size_so_far > self._size_limit:
            raise StopUpload(connection_reset=True)
        return super().receive_data_chunk(raw_data, start)


class UnknownPageNumberPaginator(Paginator):
    def __init__(self, *args, **kwargs):
        try:
            self.min_pages = max(1, int(kwargs.pop("min_pages")))
        except:
            self.min_pages = 1
        super().__init__(*args, **kwargs)

    @cached_property
    def count(self):
        return (self.min_pages + 1) * self.per_page

    def _get_page(self, *args, **kwargs):
        return UnknownEndPage(*args, **kwargs)


class UnknownEndPage(Page):
    def has_next(self):
        return len(self) == self.paginator.per_page


# For all the hackage below, see the commit log for when this code was introduced.
# In short, when Django people try to fix async code, they introduce breakage.
# Specifically, in this case: FileResponse always returns an iterator of callables
# (constructed using iter(lambda, b"")) which pull chunks from the original file-like.
# The AsgiResponse, on the other hand, always loops over this iterator asynchronously,
# which leads to the (handled, but bogusly) corner case of async code needing a sync iterator,
# which is done by slurping the entire iterator into memory. Sic.
#
# The problem was caught by ui.core.contests.tests.DatazipStreamingTestCase while upgrading
# to Django 4.2.


class OmniIter:
    def __init__(self, real):
        self.real = real

    def __iter__(self):
        return self

    def __aiter__(self):
        return self

    def __next__(self):
        return self.real.__next__()

    async def __anext__(self):
        if hasattr(self.real, "__next__"):
            try:
                return self.real.__next__()
            except StopIteration:
                raise StopAsyncIteration
        else:
            return await self.real.__anext__()


# Make sure the MRO on ReallystreamingFileResponse suits us, since the
# __mro__ attribute is readonly. See C3 linearization for why this works
# (https://www.python.org/download/releases/2.3/mro/).
class HonestlyJustAMITM(StreamingHttpResponse):
    def _set_streaming_content(self, value):
        new_iter = OmniIter(value)
        super()._set_streaming_content(new_iter)
        self._iterator = new_iter.__aiter__()
        self.is_async = True


class ReallyStreamingFileResponse(FileResponse, HonestlyJustAMITM):
    pass
