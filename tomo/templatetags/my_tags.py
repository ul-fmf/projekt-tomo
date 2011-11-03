import markdown

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

# This code is taken from https://github.com/mayoff/python-markdown-mathjax
# We put it here instead of in mdx_mathjax.py to ensure it is bundled with app.
# This is because mdx_mathjax needs to be on PYTHONPATH because of how
# markdown extensions work in python.

class MathJaxPattern(markdown.inlinepatterns.Pattern):

    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(self, r'(?<!\\)(\$\$?)(.+?)\2')

    def handleMatch(self, m):
        return markdown.AtomicString(m.group(2) + m.group(3) + m.group(2))

class MathJaxExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        # Needs to come before escape matching because \ is pretty important in LaTeX
        md.inlinePatterns.add('mathjax', MathJaxPattern(), '<escape')

register = template.Library()
md = markdown.Markdown(extensions=[MathJaxExtension()])

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

@register.filter
def get_default(h, key):
    return h.get(key, None)

@register.filter
@stringfilter
def tex_markdown(source):
    return md.convert(source)
tex_markdown.is_safe = True
