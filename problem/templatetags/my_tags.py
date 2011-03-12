from markdown import Markdown

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()
md = Markdown()

@register.filter
@stringfilter
def pymarkdown(source):
    output = ""
    strbuff = ""
    in_comment = True
    
    for line in source.splitlines():
        if line.startswith("#") and not line.startswith("#    "):
            if not in_comment:
                output += "</code></pre>\n"
                in_comment = True
            strbuff += line[1:] + "\n"
        else:
            if in_comment:
                output += md.convert(strbuff)
                strbuff = ""
                output += "<pre><code>"
                in_comment = False
            if line.startswith("#    "):
                output += line[4:] + "\n"
            else:
                output += line + "\n"

    if in_comment:
        output += md.convert(strbuff)
    else:
        output += "</code></pre>\n"

    return output

@register.filter
def get(h, key):
    return h.get(key)

@register.filter
def alpha(i):
    if 1 <= i <= 26:
        return chr(96 + i)

# @register.filter
# @stringfilter
# def pymarkdown(source):
#     source = re.sub('`', '', source)
#     return source

