import json

import markdown
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


# This code is taken from https://github.com/mayoff/python-markdown-mathjax/
# It is suppossed to be in mdx_mathjax.py, which furthermore has to be on
# PYTHONPATH because that is how markdown extensions work in Python.
#
# We, however, want to bundle it with app, that is why we copy the code here.
# We hope that the author does not mind.
class MathJaxPattern(markdown.inlinepatterns.Pattern):
    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(self, r"(?<!\\)(\$\$?)(.+?)\2")

    def handleMatch(self, m):
        node = markdown.util.etree.Element("mathjax")
        node.text = markdown.util.AtomicString(m.group(2) + m.group(3) + m.group(2))
        return node


class MathJaxExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        # Needs to come before escape matching because \ is pretty important in LaTeX
        md.inlinePatterns.add("mathjax", MathJaxPattern(), "<escape")


md = markdown.Markdown(extensions=[MathJaxExtension()])


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
