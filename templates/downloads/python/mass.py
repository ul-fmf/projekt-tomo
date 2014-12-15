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

    Check.summarize()

_check()

#####################################################################@@#
