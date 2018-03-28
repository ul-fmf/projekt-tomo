{% for attempt in history %}
# {{ attempt.part.problem.title }}, {{ attempt.part }}
# {{ attempt.history_date }}
# {{ attempt.valid }}
{{ attempt.solution|safe }}
{% endfor %}
