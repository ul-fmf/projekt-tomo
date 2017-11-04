{% load i18n %}with open(__file__, encoding='utf-8') as f:
    source = f.read()
exec(source[source.find("# =L=I=B=""R=A=R=Y=@="):])
problem = extract_problem(__file__)
Check.initialize(problem['parts'])

# =============================================================================
# {{ problem.title|safe }}{% if problem.description %}
#
# {{ problem.description|indent:"# "|safe }}{% endif %}{% for part in problem.parts.all %}
# =====================================================================@{{ part.id|stringformat:'06d'}}=
# {{ part.description|indent:"# "|safe }}{% if part.template %}
# -----------------------------------------------------------------------------
# {{ part.template|indent:"# "|safe }}{% endif %}
# =============================================================================
{{ part.solution|safe }}

Check.part()
{{ part.validation|safe }}

{% endfor %}
# # =====================================================================@000000=
# # {% blocktrans %}This is a template for a new problem part. To create a new part, uncomment
# # the template and fill in your content.
# #
# # Define a function `multiply(x, y)` that returns the product of `x` and `y`.
# # For example:
# #
# #     >>> multiply(3, 7)
# #     21
# #     >>> multiply(6, 7)
# #     42{% endblocktrans %}
# # =============================================================================
#
# def {% trans "multiply" %}(x, y):
#     return x * y
#
# Check.part()
#
# Check.equal('{% trans "multiply" %}(3, 7)', 21)
# Check.equal('{% trans "multiply" %}(6, 7)', 42)
# Check.equal('{% trans "multiply" %}(10, 10)', 100)
# Check.secret({% trans "multiply" %}(100, 100))
# Check.secret({% trans "multiply" %}(500, 123))


# ===========================================================================@=
# {% trans "Do not change this line or anything below it." %}
# =============================================================================


if __name__ == '__main__':
    _validate_current_file()

# =L=I=B=R=A=R=Y=@=

import io, json, os, re, sys, shutil, traceback, urllib.error, urllib.request

{% include 'python/check.py' %}

def extract_problem(filename):
    def strip_hashes(description):
        if description is None:
            return ''
        else:
            lines = description.strip().splitlines()
            return "\n".join(line[2:] for line in lines)

    with open(filename, encoding='utf-8') as f:
        source = f.read()
    part_regex = re.compile(
        r'# ===+@(?P<part>\d+)=\n'             # beginning of part header
        r'(?P<description>(#( [^\n]*)?\n)+?)'  # description
        r'(# ---+\n'                           # optional beginning of template
        r'(?P<template>(#( [^\n]*)?\n)*))?'    # solution template
        r'# ===+\n'                            # end of part header
        r'(?P<solution>.*?)'                   # solution
        r'^Check\.part\(\)\n'                  # beginning of validation
        r'(?P<validation>.*?)'                 # validation
        r'(?=\n(# )?# =+@)',                   # beginning of next part
        flags=re.DOTALL | re.MULTILINE
    )
    parts = [{
        'part': int(match.group('part')),
        'description': strip_hashes(match.group('description')),
        'solution': match.group('solution').strip(),
        'template': strip_hashes(match.group('template')),
        'validation': match.group('validation').strip(),
        'problem': {{ problem.id }}
    } for match in part_regex.finditer(source)]
    problem_match = re.search(
        r'^# =+\n'                             # beginning of header
        r'^# (?P<title>[^\n]*)\n'              # title
        r'(?P<description>(^#( [^\n]*)?\n)*)'  # description
        r'(?=(# )?# =+@)',                     # beginning of first part
        source, flags=re.DOTALL | re.MULTILINE)
    return {
        'title': problem_match.group('title').strip(),
        'description': strip_hashes(problem_match.group('description')),
        'parts': parts,
        'id': {{ problem.id }},
        'problem_set': {{ problem.problem_set.id }}
    }

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
            if part['part']:
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
        print('{% trans "The problem is correctly formulated." %}')
        if input('{% trans "Should I save it on the server [yes/NO]" %}') == '{% trans "yes" %}':
            print('{% trans "Saving problem to the server" %}...', end="")
            try:
                url = '{{ submission_url }}'
                token = 'Token {{ authentication_token }}'
                response = submit_problem(problem, url, token)
                if 'update' in response:
                    print('{% trans "Updating file" %}... ', end="")
                    backup_filename = backup(__file__)
                    with open(__file__, 'w', encoding='utf-8') as f:
                        f.write(response['update'])
                    print('{% trans "Previous file has been renamed to" %} {0}.'.format(backup_filename))
                    print('{% trans "If the file did not refresh in your editor, close and reopen it." %}')
            except urllib.error.URLError as response:
                message = json.loads(response.read().decode('utf-8'))
                print('\n{% trans "AN ERROR OCCURED WHEN TRYING TO SAVE THE PROBLEM!" %}')
                if message:
                    print('  ' + '\n  '.join(message.splitlines()))
                print('{% trans "Please, try again." %}')
            else:
                print('{% trans "Problem saved." %}')
        else:
            print('{% trans "Problem was not saved." %}')
    else:
        print('{% trans "The problem is not correctly formulated." %}')
