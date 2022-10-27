import json

import markdown
import mdx_math
from django.core.exceptions import PermissionDenied, ValidationError
from django.template.defaultfilters import register, stringfilter
from django.utils.safestring import mark_safe


def is_json_string_list(s):
    """
    Checks if the string s represents a list of strings in JSON.

    The function does nothing if s represents a valid list of strings,
    or raises a suitable ValidationError if not.
    """
    try:
        val = json.loads(s)
    except:
        raise ValidationError("Not a JSON value.")
    if type(val) is not list:
        raise ValidationError("Not a JSON list.")
    for x in val:
        if type(x) is not str:
            raise ValidationError("Not a JSON list of strings.")


def truncate(s, max_length=50, indicator="..."):
    """
    Returns the string s truncated to at most max_length characters.

    If s is shorter than max_length, the function returns it as it was,
    otherwise, it truncates it to max_length characters (counting the string
    indicating the truncation). If the indicator itself is longer than
    max_length, we raise a ValueError.
    """
    if len(s) <= max_length:
        return s
    elif max_length < len(indicator):
        raise ValueError("Indicator longer than maximum length.")
    else:
        return "{0}{1}".format(s[: max_length - len(indicator)], indicator)


@register.filter
@stringfilter
def indent(source, indent):
    return ("\n" + indent).join(source.splitlines())


md = markdown.Markdown(
    extensions=[mdx_math.MathExtension(enable_dollar_delimiter=True)]
)


@register.filter
@stringfilter
def latex_markdown(source):
    return mark_safe(md.convert(source))


def verify(cond):
    if not cond:
        raise PermissionDenied


@register.filter
@stringfilter
def remove_spaces(source):
    return source.replace(" ", "").replace("\n", "")
