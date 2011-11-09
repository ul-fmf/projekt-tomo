{% load my_tags %}#####################################################################@@#
# {{ problem.title }} {% if problem.description %}
#
# {{ problem.description|remove_markdown|safe }}{% endif %}
#####################################################################@@#

{{ problem.preamble|safe }}

{% for part in parts %}
################################################################@{{ part.id|stringformat:'06d'}}#
# {{ forloop.counter }}) {{ part.description|remove_markdown|safe }}
################################################################{{ part.id|stringformat:'06d'}}@#
{% with attempts|get:part.id as attempt %}{% if attempt.solution %}{{ attempt.solution|safe }}{% endif %}{% endwith %}

{% endfor %}








































































































#####################################################################@@#
# Kode pod to črto nikakor ne spreminjajte.
########################################################################

"TA VRSTICA JE PRAVILNA."
"ČE VAM R SPOROČI, DA JE V NJEJ NAPAKA, SE MOTI."
"NAPAKA JE NAJVERJETNEJE V ZADNJI VRSTICI VAŠE KODE."
"ČE JE NE NAJDETE, VPRAŠAJTE ASISTENTA."




























































.filename <- get_current_filename()

.check <- function() {
  {% include 'r/httpRequest.r' %}
  {% include 'r/rjson.r' %}
  {% include 'r/library.r' %}
  {% include 'r/check.r' %}

  .source <- paste(readLines(.filename), collapse="\n")

  matches <- regex_break(paste(
      '#{50,}@',
      '(\\d+)',
      '#.*?#{50,}\\1@#', # header
      '.*?',             # solution
      '(?=#{50,}@)',     # beginning of next part
      sep=""
  ),  c(
      '#{50,}@',
      '(\\d+)',
      '#.*#{50,}(\\d+)@#', # header
      '.*?'                #solution
  ), .source)

  check$initialize(data.frame(
    part = apply(matches, 1, function(match) as.numeric(match[2])),
    solution = apply(matches, 1, function(match) strip(match[4])),
    stringsAsFactors=FALSE
  ))

  {% for part in parts %}
  if (check$part()) {
      {{ part.validation|indent:"        "|safe }}
  }
  {% endfor %}

  check$summarize()
  {% if authenticated %}
  cat('Shranjujem rešitve na strežnik...\n')
  post <- list(
    data = '{{ data|safe }}',
    timestamp = '{{ timestamp }}',
    signature = '{{ signature }}',
    attempts = check$dump(),
    source=source
  )
  response <- postToHost('{{ request.META.SERVER_NAME }}', '{% url upload %}', post, port={{ request.META.SERVER_PORT }})
  cat(response)
  {% else %}
  cat('Rešujete kot anonimni uporabnik, zato rešitve niso shranjene.')
  {% endif %}
}

.check()
