import json
from django.core.exceptions import ValidationError


def is_json_string_list(s):
    try:
        val = json.loads(s)
    except ValueError:
        raise ValidationError('Not a JSON value.')
    if type(val) is not list:
        raise ValidationError('Not a JSON list.')
    for x in val:
        if type(x) is not unicode:
            raise ValidationError('Not a JSON list of strings.')


def shorten(s, max_length=50):
    if len(s) < max_length:
        return s
    else:
        return u'{0}...'.format(s[:50])
