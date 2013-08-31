{% load my_tags %}#######################################################################@@#
# {{ user.get_full_name }}, {{ problem.title }}
#######################################################################@@#
{{ preamble|safe }}{% for part in parts %}{% with attempts|get:part.id as attempt %}{% if attempt.correct %}
##################################################################@{{ part.id|stringformat:'06d'}}#
# {{ forloop.counter }})
# PRAVILNA REŠITEV
##################################################################{{ part.id|stringformat:'06d'}}@#
{{ attempt.solution|safe }}{% endif %}{% if not attempt.correct and attempt.solution %}
##################################################################@{{ part.id|stringformat:'06d'}}#
# {{ forloop.counter }}) 
# NAPAČNA REŠITEV: {% if attempt.error_list %}{% for error in attempt.error_list %}
# * {{ error|indent:"#   "|safe}}{% endfor %}{% else %}
# * zavrnjen izziv{% endif %}
##################################################################{{ part.id|stringformat:'06d'}}@#
{{ attempt.solution|safe }}{% endif %}{% if not attempt.solution %}
##################################################################@{{ part.id|stringformat:'06d'}}#
# {{ forloop.counter }}) 
# BREZ REŠITVE
##################################################################{{ part.id|stringformat:'06d'}}@#
{% endif %}
{% endwith %}{% endfor %}






































































































#######################################################################@@#
# Kode pod to črto nikakor ne spreminjajte.
##########################################################################

"TA VRSTICA JE PRAVILNA."
"ČE VAM PYTHON SPOROČI, DA JE V NJEJ NAPAKA, SE MOTI."
"NAPAKA JE NAJVERJETNEJE V ZADNJI VRSTICI VAŠE KODE."
"ČE JE NE NAJDETE, VPRAŠAJTE ASISTENTA."



























































import io, json, os, re, sys, shutil, traceback
from contextlib import contextmanager
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
            r'#+(?P=part)@#\n'     # end of header
            r'(?P<solution>.*?)'   # solution
            r'(?=\n#+@)',          # beginning of next part
            flags=re.DOTALL|re.MULTILINE
        ).finditer(_source)
    ])
    Check.parts[-1]['solution'] = Check.parts[-1]['solution'].rstrip()


    problem_match = re.search(
        r'#+@@#\n'           # beginning of header
        r'.*?'               # description
        r'#+@@#\n'           # end of header
        r'(?P<preamble>.*?)' # preamble
        r'(?=\n#+@)',        # beginning of first part
        _source, flags=re.DOTALL|re.MULTILINE)

    if not problem_match:
        print("NAPAKA: datoteka ni pravilno oblikovana")
        sys.exit(1)

    _preamble = problem_match.group('preamble')

    {% for part in parts %}
    if Check.part():
        try:
            {{ part.validation|indent:"            "|safe }}
            pass
        except:
            Check.error("Testi sprožijo izjemo\n  {0}", "\n  ".join(traceback.format_exc().split("\n"))[:-2])

    {% endfor %}

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
            Check.parts[k - 1]['rejection'] = e
        Check.summarize()
        if 'update' in response:
            print("Posodabljam datoteko... ", end = "")
            index = 1
            while os.path.exists('{0}.{1}'.format(_filename, index)):
                index += 1
            backup_filename = "{0}.{1}".format(_filename, index)
            shutil.copy(_filename, backup_filename)
            r = urlopen(response['update'])
            with open(_filename, 'w', encoding='utf-8') as _f:
                _f.write(r.read().decode('utf-8'))
            print("Stara datoteka je preimenovana v {0}.".format(os.path.basename(backup_filename)))
            print("Če se datoteka v urejevalniku ni osvežila, jo zaprite ter ponovno odprite.")
    except HTTPError as r:
        print('Pri shranjevanju je prišlo do napake.')
        Check.summarize()
        print('Pri shranjevanju je prišlo do napake. Poskusite znova.')
        Check.error = r.read().decode('utf-8')
    {% else %}
    Check.summarize()
    print('Naloge rešujete kot anonimni uporabnik, zato rešitve niso shranjene.')
    {% endif %}

_check()

#####################################################################@@#
