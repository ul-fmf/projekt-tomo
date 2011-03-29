{% load my_tags %}#####################################################################@@#
# {{ problem.name }} {% if problem.description %}
# 
{{ problem.description|safe }}{% endif %}
#####################################################################@@#


{% for part in problem.parts.all %}
################################################################@{{ part.id|stringformat:'06d'}}#
# Naloga {{ forloop.counter }}) {% if part.description %}
# 
{{ part.description|safe }}{% endif %}
################################################################{{ part.id|stringformat:'06d'}}@#
{% with solutions|get:part as solution %}{{ solution.solution|safe }}
{% endwith %}
{% endfor %}




































































































#####################################################################@@#
# Kode pod to črto nikakor ne spreminjajte.
########################################################################

















































"TA VRSTICA JE PRAVILNA."
"ČE VAM PYTHON SPOROČI, DA JE V NJEJ NAPAKA, SE MOTI."
"NAPAKA JE NAJVERJETNEJE V ZADNJI VRSTICI VAŠE KODE."
"ČE JE NE NAJDETE, VPRAŠAJTE ASISTENTA."



























































{% include 'python/library.py' %}

_filename = os.path.abspath(sys.argv[0])
_source, _parts = _split_file(_filename)

{{ problem.trial|safe }}
{% for part in problem.parts.all %}
{{ part.trial|safe }}
_parts[{{ forloop.counter0 }}]['trial'] = trial
{% endfor %}

_submit_solutions(_parts,
                  source=_source,
                  username='{{ username }}',
                  signature='{{ signature }}',
                  download_ip='{{ request.META.REMOTE_ADDR }}')
#####################################################################@@#
