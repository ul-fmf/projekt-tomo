{% include 'python/check.py' %}

import io, json, os, re, sys, shutil, traceback, urllib.error, urllib.request

def extract_problem(filename):
    def strip_hashes(description):
        lines = description.strip().splitlines()
        return "\n".join(line[2:] for line in lines)

    with open(filename, encoding='utf-8') as f:
        source = f.read()
    part_regex = re.compile(
        r'# =+@(?P<part>\d+)=\n'              # beginning of header
        r'(?P<description>(#( [^\n]*)?\n)+)'  # description
        r'# =+\n'                             # end of header
        r'(?P<solution>.*?)'                  # solution
        r'^Check\.part\(\)\n'                 # beginning of validation
        r'(?P<validation>.*?)'                # validation
        r'(?=\n# =+@)',                       # beginning of next part
        flags=re.DOTALL | re.MULTILINE
    )
    parts = [{
        'part': int(match.group('part')),
        'description': strip_hashes(match.group('description')),
        'solution': match.group('solution').strip(),
        'validation': match.group('validation').strip(),
        'problem': {{ problem.id }}
    } for match in part_regex.finditer(source)]
    # The last solution extends all the way to the validation code,
    # so we strip any trailing whitespace from it.
    parts[-1]['solution'] = parts[-1]['solution'].rstrip()
    problem_match = re.search(
        r'^# =+\n'                             # beginning of header
        r'^# (?P<title>[^\n]*)\n'              # title
        r'(?P<description>(^#( [^\n]*)?\n)*)'  # description
        r'# =+@',                              # beginning of first part
        source, flags=re.DOTALL | re.MULTILINE)
    return {
        'title': problem_match.group('title').strip(),
        'description': strip_hashes(problem_match.group('description')),
        'parts': parts,
        'id': {{ problem.id|default:"None" }}
    }


filename = os.path.abspath(sys.argv[0])
problem = extract_problem(filename)
Check.initialize(problem['parts'])

# =============================================================================
# {{ problem.title }}{% if problem.description %}
#
# {{ problem.description|indent:"# "|safe }}{% endif %}{% for part in problem.parts.all %}
# =====================================================================@{{ part.id|stringformat:'06d'}}=
# {{ part.description|indent:"# "|safe }}
# =============================================================================
{{ part.solution|safe }}

Check.part()
{{ part.validation|safe }}

{% endfor %}

# ===========================================================================@=

def _validate_current_file():
    def backup(filename):
        backup_filename = None
        suffix = 1
        while not backup_filename or os.path.exists(backup_filename):
            backup_filename = '{0}.{1}'.format(filename, suffix)
            suffix += 1
        shutil.copy(filename, backup_filename)
        return backup_filename

    def submit_problem(problem, url, token):
        for part in problem['parts']:
            part['secret'] = [x for (x, _) in part['secret']]
            part['id'] = part['part']
            del part['part']
            del part['feedback']
            del part['valid']
        data = json.dumps(problem).encode('utf-8')
        headers = {
            'Authorization': token,
            'content-type': 'application/json'
        }
        request = urllib.request.Request(url, data=data, headers=headers)
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))

    Check.summarize()
    if all(part['valid'] for part in problem['parts']):
        print('Shranjujem rešitve na strežnik... ', end="")
        try:
            url = '{{ submission_url }}'
            token = 'Token {{ authentication_token }}'
            response = submit_problem(problem, url, token)
        except urllib.error.URLError:
            print('PRI SHRANJEVANJU JE PRIŠLO DO NAPAKE! Poskusite znova.')
        else:
            print('Rešitve so shranjene.')

_validate_current_file()
