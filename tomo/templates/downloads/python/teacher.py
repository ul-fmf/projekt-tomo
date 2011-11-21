#################################################################
# To je datoteka, s katero pripravite nalogo.
# Vsebina naloge je spodaj, za definicijo razreda Check.
#################################################################
{% load my_tags %}

import json, os, re, sys, shutil
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
{% include 'downloads/python/check.py' %}

_filename = os.path.abspath(sys.argv[0])
with open(_filename, encoding='utf-8') as f:
    source = f.read()

Check.initialize([
    {
        'part': int(match.group('part')),
        'description': "\n".join(s[2:] for s in match.group('description').strip().splitlines()),
        'solution': match.group('solution').strip(),
        'validation': match.group('validation').strip(),
    } for match in re.compile(
        r'^#+@(?P<part>\d+)#\n'               # beginning of header
        r'(?P<description>(^#( [^\n]*)?\n)*)' # description
        r'^#+\1@#\n'                          # end of header
        r'(?P<solution>.*?)'                  # solution
        r'^Check\.part\(\)\n'                 # beginning of validation
        r'(?P<validation>.*?)'                # validation
        r'^(# )?(?=#+@)',                     # beginning of next part
        flags=re.DOTALL|re.MULTILINE
    ).finditer(source)
])

problem_match = re.search(
    r'^#+@@#\n'                           # beginning of header
    r'^# (?P<title>[^\n]*)\n'             # title
    r'^(#\s*\n)*'                         # empty rows
    r'(?P<description>(^#( [^\n]*)?\n)*)' # description
    r'^#+@@#\n'                           # end of header
    r'(?P<preamble>.*?)'                  # preamble
    r'^(# )?(?=#+@)',                     # beginning of first part
    source, flags=re.DOTALL|re.MULTILINE)

if not problem_match:
    print("NAPAKA: datoteka ni pravilno oblikovana")
    sys.exit(1)

title = problem_match.group('title').strip()
description = "\n".join(s[2:] for s in problem_match.group('description').strip().splitlines())
preamble = problem_match.group('preamble').strip()

###################################################################
# Od tu naprej je navodilo naloge

################################################################@@#
# {{ problem.title }} {% if problem.description %}
#
# {{ problem.description|indent:"# "|safe }}{% endif %}
################################################################@@#

{{ problem.preamble|safe }}

{% for part in parts %}
################################################################@{{ part.id|stringformat:'06d'}}#
# {{ part.description|indent:"# "|safe }}
################################################################{{ part.id|stringformat:'06d'}}@#
{{ part.solution|safe }}

Check.part()
{{ part.validation|safe }}

{% endfor %}

# ################################################################@000000#
# # To je predloga za novo podnalogo. Tu vpisite besedilo podnaloge.
# ################################################################000000@#
#
# sem napisite resitev
#
# Check.part()
#
# Check.compare(...)
#
# Check.challenge(...)

#####################################################################@@#
# Od tu naprej ničesar ne spreminjajte.

Check.summarize()
if any(part.get('errors') for part in Check.parts):
    print('Naloge so napačno sestavljene.')
else:
    print('Naloge so pravilno sestavljene.')
    if input('Ali jih shranim na strežnik? [da/NE]') == 'da':
        print('Shranjujem naloge...')
        post = json.dumps({
            'data': '{{ data|safe }}',
            'signature': '{{ signature }}',
            'title': title,
            'description': description,
            'preamble': preamble,
            'parts': Check.parts,
        }).encode('utf-8')
        try:
            r = urlopen('http://{{ request.META.HTTP_HOST }}{% url teacher_upload %}', post)
            response = json.loads(r.read().decode('utf-8'))
            print(response['message'])
            if 'update' in response:
                r = urlopen(response['update'])
                shutil.copy(_filename, _filename + ".orig")
                with open(_filename, 'w', encoding='utf-8') as f:
                    f.write(r.read().decode('utf-8'))
        except HTTPError:
            print('Pri shranjevanju je prišlo do napake. Poskusite znova.')
    else:
        print('Naloge niso bile shranjene.')
