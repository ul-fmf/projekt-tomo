import json
from django.core.exceptions import ValidationError


def is_json_string_list(s):
    '''
    Checks if the string s represents a list of strings in JSON.

    The function does nothing if s represents a valid list of strings,
    or raises a suitable ValidationError if not.
    '''
    try:
        val = json.loads(s)
    except:
        raise ValidationError('Not a JSON value.')
    if type(val) is not list:
        raise ValidationError('Not a JSON list.')
    for x in val:
        if type(x) is not unicode:
            raise ValidationError('Not a JSON list of strings.')


def truncate(s, max_length=50, indicator="..."):
    '''
    Returns the string s truncated to at most max_length characters.

    If s is shorter than max_length, the function returns it as it was,
    otherwise, it truncates it to max_length characters (counting the string
    indicating the truncation). If the indicator itself is longer than
    max_length, we raise a ValueError.
    '''
    if len(s) <= max_length:
        return s
    elif max_length < len(indicator):
        raise ValueError('Indicator longer than maximum length.')
    else:
        return u'{0}{1}'.format(s[:max_length - len(indicator)], indicator)
