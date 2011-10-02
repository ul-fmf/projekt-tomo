from markdown import Markdown

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()
md = Markdown()

@register.filter
@stringfilter
def markdown2py(source):
    lines = source.splitlines()
    lines = [line[4:] if line.startswith("    ") else line for line in lines]
    lines = [line.replace('`', '') for line in lines]
    return "\n# ".join(lines)

@register.filter
@stringfilter
def indent(source, indent):
    return ("\n" + indent).join(source.splitlines())

@register.filter
def get(h, key):
    return h.get(key)
