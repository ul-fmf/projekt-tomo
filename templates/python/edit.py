{% load my_tags %}{% include 'python/check.py' %}
with open(os.path.abspath(sys.argv[0])) as f:
    source = f.read()

Check.initialize([
    {
        'part': int(match.group(1)),
        'description': "\n".join(s[2:] for s in match.group(2).strip().splitlines()),
        'solution': match.group(3).strip(),
        'validation': match.group(4).strip(),
    } for match in re.compile(
        r'#+@(\d+)#'        # beginning of header
        r'(.*?)'            # description
        r'#+\1@#'           # end of header
        r'(.*?)'            # solution
        r'Check\.part\(\)'  # beginning of validation
        r'(.*?)'            # validation
        r'(?=#{50,}@)',     # beginning of next part
        flags=re.DOTALL|re.MULTILINE
    ).finditer(source)
])

problem_match = re.search(
    r'#{50,}@@#'        # beginning of header
    r'\n#(.*?)\n'       # title
    r'(.*?)'            # description
    r'#{50,}@@#'        # end of header
    r'(.*?)'            # preamble
    r'(?=#{50,}@)',     # beginning of first part
    source, flags=re.DOTALL|re.MULTILINE)
title = problem_match.group(1).strip()
description = "\n".join(s[2:] for s in problem_match.group(2).strip().splitlines())
preamble = problem_match.group(3).strip()
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

#####################################################################@@#

Check.summarize()
if all('errors' not in part or not part['errors'] for part in Check.parts):
    print('Naloge so pravilno sestavljene.')
    if input('Ali jih shranim na strežnik? [da/NE]') == 'da':
        print('Shranjujem naloge...')
        post = urlencode({
            'data': '{{ data|safe }}',
            'signature': '{{ signature }}',
            'title': title,
            'description': description,
            'preamble': preamble,
            'parts': Check.dump(),
        }).encode()
        try:
            r = urlopen('http://{{ request.META.HTTP_HOST }}{% url update %}', post)
            print(r.read().decode())
        except HTTPError:
            print('Pri shranjevanju je prišlo do napake. Poskusite znova.')
    else:
        print('Naloge niso bile shranjene.')
else:
    print('Naloge so napačno sestavljene.')
