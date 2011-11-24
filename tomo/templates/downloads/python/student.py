{% load my_tags %}#####################################################################@@#
# {{ problem.title }} {% if problem.description %}
#
# {{ problem.description|remove_markdown|safe }}{% endif %}
#####################################################################@@#
{{ preamble|safe }}{% for part in parts %}
################################################################@{{ part.id|stringformat:'06d'}}#
# {{ forloop.counter }}) {{ part.description|remove_markdown|safe }}
################################################################{{ part.id|stringformat:'06d'}}@#
{% with attempts|get:part.id as attempt %}{% if attempt.solution %}{{ attempt.solution|safe }}{% else %}

{% endif %}{% endwith %}{% endfor %}








































































































#####################################################################@@#
# Kode pod to črto nikakor ne spreminjajte.
########################################################################

"TA VRSTICA JE PRAVILNA."
"ČE VAM PYTHON SPOROČI, DA JE V NJEJ NAPAKA, SE MOTI."
"NAPAKA JE NAJVERJETNEJE V ZADNJI VRSTICI VAŠE KODE."
"ČE JE NE NAJDETE, VPRAŠAJTE ASISTENTA."



























































import json, os, re, sys, shutil
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
{% include 'downloads/python/check.py' %}

def _check():
    _filename = os.path.abspath(sys.argv[0])
    with open(_filename, encoding='utf-8') as _f:
        _source = _f.read()

    Check.initialize([
        {
            'part': int(match.group('part')),
            'solution': match.group('solution')
        } for match in re.compile(
            r'#+@(?P<part>\d+)#\n' # beginning of header
            r'.*?'                 # description
            r'#+\1@#\n'            # end of header
            r'(?P<solution>.*?)'   # solution
            r'(?=\n#+@)',            # beginning of next part
            flags=re.DOTALL|re.MULTILINE
        ).finditer(_source)
    ])
    Check.parts[-1]['solution'] = Check.parts[-1]['solution'].rstrip()


    problem_match = re.search(
        r'#+@@#\n'           # beginning of header
        r'.*?'               # description
        r'#+@@#\n'           # end of header
        r'(?P<preamble>.*?)' # preamble
        r'(?=\n#+@)',          # beginning of first part
        _source, flags=re.DOTALL|re.MULTILINE)

    if not problem_match:
        print("NAPAKA: datoteka ni pravilno oblikovana")
        sys.exit(1)

    _preamble = problem_match.group('preamble')

    {% for part in parts %}
    if Check.part():
        {{ part.validation|indent:"        "|safe }}
    {% endfor %}

    Check.summarize()
    {% if authenticated %}
    print('Shranjujem rešitve na strežnik... ', end = "")
    post = json.dumps({
        'data': '{{ data|safe }}',
        'signature': '{{ signature }}',
        'preamble': _preamble,
        'attempts': Check.parts,
        'source': _source,
    }).encode('utf-8')
    try:
        r = urlopen('http://{{ request.META.SERVER_NAME }}:{{ request.META.SERVER_PORT }}{% url student_upload %}', post)
        response = json.loads(r.read().decode('utf-8'))
        print('Rešitve so shranjene.')
        for (k, e) in response['rejected']:
            print("Rešitev podnaloge {0} je zavrnjena ({1}).".format(k, e))
        if 'update' in response:
            print("Na voljo je nova različica... Posodabljam datoteko... ", end = "")
            index = 1
            while os.path.exists('{0}.{1}'.format(_filename, index)):
                index += 1
            backup_filename = "{0}.{1}".format(_filename, index)
            shutil.copy(_filename, backup_filename)
            r = urlopen(response['update'])
            with open(_filename, 'w', encoding='utf-8') as f:
                f.write(r.read().decode('utf-8'))
            print("Datoteka je posodobljena.")
            print("Kopija stare datoteke je v {0}.".format(backup_filename))
            print("Če se datoteka v urejevalniku ni osvežila, jo zaprite ter ponovno odprite.")
    except HTTPError as r:
        print('Pri shranjevanju je prišlo do napake. Poskusite znova.')
        Check.error = r.read().decode('utf-8')
    {% else %}
    print('Naloge rešujete kot anonimni uporabnik, zato rešitve niso shranjene.')
    {% endif %}

_check()

#####################################################################@@#
