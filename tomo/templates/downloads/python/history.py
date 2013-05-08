{% load my_tags %}{% for submission in submissions %}
################################################################################
# {{ submission.timestamp }}
################################################################################
{% for part in parts %}{% with submission.attempts|get:part.id as attempt %}{% if attempt.correct %}
# {{ forloop.counter }}) PRAVILNA REŠITEV
{{ attempt.solution.strip|safe }}{% endif %}{% if not attempt.correct and attempt.solution %}
# {{ forloop.counter }}) NAPAČNA REŠITEV: {% if attempt.error_list %}{% for error in attempt.error_list %}
# * {{ error|safe|indent:"#   "}}{% endfor %}{% else %}
# * zavrnjen izziv{% endif %}
{{ attempt.solution.strip|safe }}{% endif %}{% if not attempt.solution %}
# {{ forloop.counter }}) BREZ REŠITVE
{% endif %}
{% endwith %}{% endfor %}

{% endfor %}
