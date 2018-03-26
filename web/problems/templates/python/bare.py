{% for part, attempt in parts %}
{% if attempt %}
{{ attempt.solution|safe }}
{% endif %}
{% endfor %}
