# {{ problem.title|safe }} ({{ user.get_full_name }}){% for part, attempt in parts %}
# {{ forloop.counter }}. podnaloga
{% if attempt %}{{ attempt.solution|safe }}{% endif %}{% endfor %}
