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


def _split_file(filename):
    with open(filename) as f:
        source = f.read()

    part_regex = re.compile(
        r'(#{50,}@(\d+)#' # beginning of header
        r'.*?Naloga (.+?)\)' # part label
        r'.*?#{50,}\2@#)' # end of header
        r'(.*?)(?=#{50,}@)', # body
        flags=re.DOTALL|re.MULTILINE
    )
    def part(part_match):
        start = part_match.start() + len(part_match.group(1))
        end = part_match.end()
        return {
            'id': int(part_match.group(2)),
            'label': part_match.group(3),
            'start': start,
            'end': end,
            'solution': part_match.group(0),
            'attempted': bool(source[start:end].strip())
        }

    parts = [part(part_match) for part_match in part_regex.finditer(source)]
    
    return source, parts

def _run_trial(trial, solution):
    global _warn
    errors = []
    h = md5()
    _warn = lambda msg: errors.append(msg)
    for x in trial(solution):
        h.update(str(x).encode('utf-8'))
    return h.hexdigest(), errors

def _submit_solutions(parts, source, username, signature, download_ip):
    data = {
        'username': username,
        'signature': signature,
        'download_ip': download_ip,
        'source': source
    }
    for part in parts:
        label = part['label']
        if not part['attempted']:
            print('Naloga {0}) je brez rešitve.'.format(label))
        else:
            part_id = part['id'] if part['id'] else -i
            data['{0}_label'.format(part_id)] = part['label']
            data['{0}_start'.format(part_id)] = part['start']
            data['{0}_end'.format(part_id)] = part['end']
            random.seed(username)
            secret, errors = _run_trial(part['trial'], part['solution'])
            if errors:
                print('Naloga {0}) je napačno rešena:'.format(label))
                print('- ' + '\n- '.join(errors))
            else:
                print('Naloga {0}) je pravilno rešena.'.format(label))
                data['{0}_secret'.format(part_id)] = secret
    print('Shranjujem rešitve...')
    post = urlencode(data).encode('utf8')
    try:
        r = urlopen('http://{{ request.META.HTTP_HOST }}{% url upload_solution problem.id %}', post)
        contents = r.read()
    except HTTPError as error:
        contents = error.read()
    print(contents.decode())


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
