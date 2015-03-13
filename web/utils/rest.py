import json
from rest_framework.fields import Field


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
