# =============================================================================
# {{ problem.title|safe }} ({{ user.get_full_name }}){% for part, attempt in parts %}
# =====================================================================@{{ part.id|stringformat:'06d'}}=
# {{ forloop.counter }}. podnaloga
# {% if not attempt %}BREZ REŠITVE{% elif attempt.valid %}VELJAVNA REŠITEV{% else %}NEVELJAVNA REŠITEV{% endif %}{% if attempt and attempt.feedback_list %}{% for feedback in attempt.feedback_list %}
# - {{ feedback|indent:"#   "|safe }}{% endfor %}{% endif %}
# =============================================================================
{% if attempt %}{{ attempt.solution|safe }}{% endif %}{% endfor %}




































































































# ============================================================================@

'Če vam Python sporoča, da je v tej vrstici sintaktična napaka,'
'se napaka v resnici skriva v zadnjih vrsticah vaše kode.'

'Kode od tu naprej NE SPREMINJAJTE!'


















































import io, json, os, re, sys, shutil, traceback, urllib.error, urllib.request


{% include 'python/check.py' %}

def _validate_current_file():
    def extract_parts(filename):
        with open(filename, encoding='utf-8') as f:
            source = f.read()
        part_regex = re.compile(
            r'# =+@(?P<part>\d+)=\n'  # beginning of header
            r'(#( [^\n]*)?\n)+'       # description
            r'# =+\n'                 # end of header
            r'(?P<solution>.*?)'      # solution
            r'(?=\n# =+@)',           # beginning of next part
            flags=re.DOTALL | re.MULTILINE
        )
        parts = [{
            'part': int(match.group('part')),
            'solution': match.group('solution')
        } for match in part_regex.finditer(source)]
        # The last solution extends all the way to the validation code,
        # so we strip any trailing whitespace from it.
        parts[-1]['solution'] = parts[-1]['solution'].rstrip()
        return parts

    filename = os.path.abspath(sys.argv[0])
    file_parts = extract_parts(filename)
    Check.initialize(file_parts)
{% for part, _ in parts %}
    if Check.part():
        try:
            {{ part.validation|default:"pass"|indent:"            "|safe }}
        except:
            Check.error("Testi sprožijo izjemo\n  {0}",
                        "\n  ".join(traceback.format_exc().split("\n"))[:-2])
{% endfor %}
    Check.summarize()

if __name__ == '__main__':
    _validate_current_file()
