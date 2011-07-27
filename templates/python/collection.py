####################################################################@@@#
# {{ collection.name }} {% if collection.description %}
# 
{{ collection.description|safe }}{% endif %}
####################################################################@@@#

{% for problem in collection.modified_problems %}
#####################################################################@@#
# {{ forloop.counter }}. {{ problem.name }} {% if problem.description %}
# 
{{ problem.description|safe }}{% endif %}
#####################################################################@@#
{% for part in problem.modified_parts %}
################################################################@{{ part.id|stringformat:'06d'}}#
# {{ forloop.parentloop.counter }}.{{ forloop.counter }}. {% if part.description %}
{{ part.description|safe }}{% endif %}
################################################################{{ part.id|stringformat:'06d'}}@#
{{ part.user_solution|safe }}

{% endfor %}
{% endfor %}








































































































#####################################################################@@#
# Kode pod to črto nikakor ne spreminjajte.
########################################################################

"TA VRSTICA JE PRAVILNA."
"ČE VAM PYTHON SPOROČI, DA JE V NJEJ NAPAKA, SE MOTI."
"NAPAKA JE NAJVERJETNEJE V ZADNJI VRSTICI VAŠE KODE."
"ČE JE NE NAJDETE, VPRAŠAJTE ASISTENTA."



























































{% include 'python/library.py' %}
_trials = {}
{% for problem in collection.problems.all %}
{{ problem.preamble|safe }}
{% for part in problem.parts.all %}
{{ part.trial|safe }}
# XXX THIS COUNTER IS NOT GOOD
_trials[{{ part.id }}] = trial
{% endfor %}
{% endfor %}

def _submit_solutions():
    with open(os.path.abspath(sys.argv[0])) as f:
        source = f.read()

    part_regex = re.compile(
        r'(#{50,}@(\d+)#' # beginning of header
        r'.*?'            # header
        r'#{50,}\2@#)'    # end of header
        r'(.*?)'          # solution
        r'(?=#{50,}@)',   # beginning of next part
        flags=re.DOTALL|re.MULTILINE
    )
    username = '{{ username }}'
    solutions = {}

    def _run_trial(trial, solution):
        global _warn
        errors = []
        h = md5()
        _warn = lambda msg: errors.append(msg)
        for x in trial(solution):
            h.update(str(x).encode('utf-8'))
        return h.hexdigest(), errors

    for part_match in part_regex.finditer(source):
        part_id = int(part_match.group(2))
        solution = part_match.group(3).strip()
        label = "12.34"
        if not solution:
            print('Naloga {0} je brez rešitve.'.format(label))
        else:
            random.seed(username)
            secret, errors = _run_trial(_trials[part_id], solution)
            if errors:
                print('Naloga {0} je napačno rešena'.format(label))
                print('- ' + '\n- '.join(errors))
            else:
                print('Naloga {0} je pravilno rešena.'.format(label))
        solutions[part_id] = {
            'solution': solution,
            'label': label,
            'attempted': bool(solution),
            'secret': secret
        }

    print('Shranjujem rešitve...')
    post = urlencode({
        'username': username,
        'signature': '{{ signature }}',
        'download_ip': '{{ request.META.REMOTE_ADDR }}',
        'source': source,
        'solutions': json.dumps(solutions)
    }).encode('utf8')
    try:
        r = urlopen('http://{{ request.META.HTTP_HOST }}{% url upload_solution collection.id %}', post)
        contents = r.read()
    except HTTPError as error:
        contents = error.read()
    print(contents.decode())

_submit_solutions()

#####################################################################@@#
