import re

import markdown
import mdx_math
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

# from utils import MathJaxExtension

register = template.Library()

renderer = markdown.Markdown(
    extensions=[mdx_math.MathExtension(enable_dollar_delimiter=True)]
)

INLINE_CODE = re.compile(r"`([^`]+)`")
CODE_BLOCK = re.compile(r"( {4}.*\n?)+")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
ITALIC = re.compile(r"\*([^*`]+)\*")
URL = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
LIST = re.compile(r"((\n- .*)+)")


def itemizer(matchobj):
    content = [
        "  \item " + g + "\n" for g in matchobj.group(0).strip("\n- ").split("\n- ")
    ]
    return "\\begin{itemize}\n%s\\end{itemize}" % "".join(content)


def codeblock(matchobj):
    code = matchobj.group(0).rstrip("\n") + "\n"
    return "\\begin{minted}{Python}\n%s\\end{minted}" % code


@register.filter
@stringfilter
def md2tex(md):
    """Very bad converter from markdown to tex."""
    md = BOLD.sub(r"\\textbf{\1}", md)
    md = ITALIC.sub(r"\\textit{\1}", md)
    md = INLINE_CODE.sub(r"\\py{\1}", md)
    md = CODE_BLOCK.sub(codeblock, md)
    md = URL.sub(r"\1 (\\url{\2})", md)
    md = LIST.sub(itemizer, md)
    md = md.replace("\nPrimer:", "\n\\Primer")
    return mark_safe(md)
