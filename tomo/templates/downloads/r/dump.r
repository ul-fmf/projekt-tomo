{% load my_tags %}# =============================================================================
# PREDMET: {{ problem.problem_set.course.name|safe }}
# SKLOP: {{ problem.problem_set.title|safe }}
# ZNAČKE: {% if problem.preamble %}
# PREAMBULA (tega novi Tomo ne podpira več):
# {{ problem.preamble|indent:"# "|safe }}{% endif %}
# =============================================================================
# {{ problem.title|safe }} {% if problem.description %}
#
# {{ problem.description|indent:"# "|safe }}{% endif %}{% for part in parts %}
# =====================================================================@000000=
# {{ part.description|indent:"# "|safe }}
# =============================================================================
{{ part.solution|safe }}

check$part()
{{ part.validation|safe }}

{% endfor %}

# ===========================================================================@=

Check.summarize()
