import json
from django.utils.text import slugify
from rest_framework.fields import Field
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer
from .views import plain_text


class JSONStringField(Field):
    """
    Store a JSON object in a TextField.
    When object is received store its json dump.
    When object is retrieved load JSON object from string representation.
    """
    def to_internal_value(self, data):
        return json.dumps(data)

    def to_representation(self, value):
        return json.loads(value)


class DownloadMixin(object):
    @detail_route(methods=['get'])
    def download(self, request, pk=None):
        o = self.get_queryset().get(pk=pk)
        serializer = self.get_serializer(o)
        json = JSONRenderer().render(serializer.data,
                                     renderer_context={'indent': 4})
        filename = '{0}.txt'.format(slugify(o.title))
        response = plain_text(filename, json)
        return response
