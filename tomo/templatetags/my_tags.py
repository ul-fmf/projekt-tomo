import markdown

from django import template
from django.template.defaultfilters import stringfilter, register


# This code is taken from https://github.com/mayoff/python-markdown-mathjax/
# It is suppossed to be in mdx_mathjax.py, which furthermore has to be on
# PYTHONPATH because that is how markdown extensions work in Python.
#
# We, however, want to bundle it with app, that is why we copy the code here.
# We hope that the author does not mind.

class MathJaxPattern(markdown.inlinepatterns.Pattern):
    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(self, r'(?<!\\)(\$\$?)(.+?)\2')

    def handleMatch(self, m):
        node = markdown.util.etree.Element('mathjax')
        node.text = markdown.util.AtomicString(m.group(2) + m.group(3) + m.group(2))
        return node

class MathJaxExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        # Needs to come before escape matching because \ is pretty important in LaTeX
        md.inlinePatterns.add('mathjax', MathJaxPattern(), '<escape')

register = template.Library()
md = markdown.Markdown(extensions=[MathJaxExtension()])


@register.filter
@stringfilter
def tex_markdown(source):
    return md.convert(source)
tex_markdown.is_safe = True

@register.filter
@stringfilter
def remove_markdown(source):
    lines = source.splitlines()
    lines = [line[4:] if line.startswith("    ") else line for line in lines]
    lines = [line.replace('`', '') for line in lines]
    return "\n# ".join(lines)

@register.simple_tag
def koncnica(stevilo, ednina, dvojina, trojina, mnozina):
    ostanek = stevilo % 100
    if ostanek == 1:
        koncnica = ednina
    elif ostanek == 2:
        koncnica = dvojina
    elif ostanek == 3 or ostanek == 4:
        koncnica = trojina
    else:
        koncnica = mnozina
    return koncnica

@register.filter
@stringfilter
def indent(source, indent):
    return ("\n" + indent).join(source.splitlines())

@register.filter
def get(d, key):
    return d.get(key, None)

