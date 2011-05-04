{% load my_tags %}#####################################################################@@#
# {{ problem.name }} {% if problem.description %}
# 
{{ problem.description|safe }}{% endif %}
#####################################################################@@#

{{ problem.trial|safe }}

{% for part in problem.parts.all %}
################################################################@{{ part.id|stringformat:'06d'}}#
{{ part.description|safe }}
################################################################{{ part.id|stringformat:'06d'}}@#
{{ part.solution|safe }}

{{ part.trial|safe }}

{% endfor %}


#####################################################################@@#
# Kode pod to črto nikakor ne spreminjajte.
########################################################################


import inspect
import math
import random





from hashlib import md5
import os, re, random, sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

def _split_file(filename):
    with open(filename) as f:
        source = f.read()

    part_regex = re.compile(
        r'#+@(\d+|\?)#' # beginning of header
        r'(.*?)' # description
        r'\n#+\1@#' # end of header
        r'(.*?)' # solution
        r'(def trial.+?)' # trial
        r'(?=#+@)', # body
        flags=re.DOTALL|re.MULTILINE
    )
    def part(part_match):
        return {
            'id': int(part_match.group(1)) if part_match.group(1) != "?" else None,
            'description': part_match.group(2).strip(),
            'solution': part_match.group(3).strip(),
            'trial': part_match.group(4).strip()
        }

    parts = [part(part_match) for part_match in part_regex.finditer(source)]
    
    return source, parts

def _equal(example, expected, message=None):
    global _warn
    if not message:
        message = 'Ukaz {0} vrne {1!r} namesto {2!r}.'
    answer = eval(example)
    if answer != expected:
        _warn(message.format(example, answer, expected))

def check_function(name, argsnum):
    """ Preveri, če je metoda name definirana in sprejme argsnum argumentov."""  
    if name not in globals():
        _warn("Funkcija {0} ni definirana.".format(name))
        return False
    func = eval(name)
    if argsnum != -1 and len(inspect.getargspec(func)[0]) != argsnum:
        _warn("Funkcija {2} mora namesto {0} sprejeti {1} argumentov.".format(len(inspect.getargspec(func)[0]), argsnum, name))
        return False
    return True


def _run_trial(part):
    global _warn
    env = {}
    exec(part['trial'], globals(), env)
    errors = []
    h = md5()
    _warn = lambda msg: errors.append(msg)
    for x in env['trial'](part['solution']):
        h.update(str(x).encode('utf-8'))
    return h.hexdigest(), errors
    

def _submit_solutions(parts, source, username, signature, download_ip):
    data = {
        'username': username,
        'signature': signature,
        'download_ip': download_ip,
        'source': source
    }
    ids = []
    correct = True
    for label, part in enumerate(parts):
        part_id = part['id'] if part['id'] else -label
        ids.append(part_id)
        data['{0}_description'.format(part_id)] = part['description']
        data['{0}_solution'.format(part_id)] = part['solution']
        data['{0}_trial'.format(part_id)] = part['trial']
        random.seed(username)
        secret, errors = _run_trial(part)
        if errors:
            print('Naloga {0}) je napačno sestavljena:'.format(label + 1))
            print('- ' + '\n- '.join(errors))
            correct = False
        else:
            print('Naloga {0}) je pravilno sestavljena.'.format(label + 1))
            data['{0}_secret'.format(part_id)] = secret
    data['problem_ids'] = ",".join([str(i) for i in ids])
    if correct:
        print('Naloge so pravilno sestavljene.')
        if input('Ali jih shranim na strežnik? [da/NE]') is 'da':
            print('Shranjujem naloge...')
            post = urlencode(data)
            try:
                r = urlopen('http://{{ request.META.HTTP_HOST }}{% url upload_problem problem.id %}', post)
                contents = r.read()
            except HTTPError as error:
                contents = error.read()
            print(contents.decode())
        else:
            print('Naloge niso shranjene.')
    else:
        print('Naloge vsebujejo napake.')

_filename = os.path.abspath(sys.argv[0])
_source, _parts = _split_file(_filename)

_submit_solutions(_parts, _source, '{{ username }}', '{{ signature }}', '')

