{% load my_tags %}#######################################################################@@#
# {{ problem.title }}
#######################################################################@@#
{% for part in parts %}
##################################################################@{{ part.id|stringformat:'06d'}}#
# {{ forloop.counter }})
##################################################################{{ part.id|stringformat:'06d'}}@#
{% with attempts|get:part.id as attempt %}{% if attempt.solution %}{{ attempt.solution|safe }}{% else %}

{% endif %}{% endwith %}{% endfor %}
