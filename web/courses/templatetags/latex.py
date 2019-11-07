import re

import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from utils import MathJaxExtension

register = template.Library()

renderer = markdown.Markdown(extensions=[MathJaxExtension()])

INLINE_CODE = re.compile(r"`([^`]+)`")
CODE_BLOCK = re.compile(r"( {4}.*\n?)+")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
ITALIC = re.compile(r"\*([^*`]+)\*")
URL = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
LIST = re.compile(r"((\n- .*)+)")

def itemizer(matchobj):
    content = ["  \item " + g + "\n" for g in matchobj.group(0).strip('\n- ').split('\n- ')]
    return "\\begin{itemize}\n%s\\end{itemize}" % ''.join(content)


@register.filter
@stringfilter
def md2tex(md):
    """Very bad converter from markdown to tex."""
    md = BOLD.sub(r"\\textbf{\1}", md)
    md = ITALIC.sub(r"\\textit{\1}", md)
    md = INLINE_CODE.sub(r"\\py{\1}", md)
    md = CODE_BLOCK.sub(r"\\begin{minted}{Python}\n\g<0>\\end{minted}", md)
    md = URL.sub(r"\1 (\\url{\2})", md)
    md = LIST.sub(itemizer, md)
    return mark_safe(md)

