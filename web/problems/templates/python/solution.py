{% load i18n %}# =============================================================================
# {{ problem.title|safe }}{% if problem.description %}
#
# {{ problem.description|indent:"# "|safe }}{% endif %}{% for part, solution in parts %}
# =====================================================================@{{ part.id|stringformat:'06d'}}=
# {{ forloop.counter }}. podnaloga
# {{ part.description|indent:"# "|safe }}
# =============================================================================
{{ solution|safe }}{% endfor %}

# ============================================================================@

import json
import os
import re
import shutil
import sys
import traceback

{% include 'python/check.py' %}

def _validate_current_file():
    def extract_parts(filename):
        with open(filename, encoding='utf-8') as f:
            source = f.read()
        part_regex = re.compile(
            r'# =+@(?P<part>\d+)=\s*\n' # beginning of header
            r'(\s*#( [^\n]*)?\n)+?'     # description
            r'\s*# =+\s*?\n'            # end of header
            r'(?P<solution>.*?)'        # solution
            r'(?=\n\s*# =+@)',          # beginning of next part
            flags=re.DOTALL | re.MULTILINE
        )
        parts = [{
            'part': int(match.group('part')),
            'solution': match.group('solution')
        } for match in part_regex.finditer(source)]
        # The last solution extends all the way to the validation code,
        # so we strip any trailing whitespace from it.
        parts[-1]['solution'] = parts[-1]['solution'].rstrip()
        return parts

    filename = os.path.abspath(sys.argv[0])
    file_parts = extract_parts(filename)
    Check.initialize(file_parts)
{% for part, _ in parts %}
    if Check.part():
        try:
            {{ part.validation|default:"pass"|indent:"            "|safe }}
        except:
            Check.error("Testi sprožijo izjemo\n  {0}",
                        "\n  ".join(traceback.format_exc().split("\n"))[:-2])
{% endfor %}
    Check.summarize()

if __name__ == '__main__':
    _validate_current_file()
