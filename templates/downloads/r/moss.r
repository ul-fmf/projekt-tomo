{% load my_tags %}{% for part in parts %}
# {{ forloop.counter }})
{% with attempts|get:part.id as attempt %}{% if attempt.solution %}{{ attempt.solution|safe }}{% else %}

{% endif %}{% endwith %}{% endfor %}
