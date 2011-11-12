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
      '#+@(\\d+)#\n', # beginning of header
      '.*?',          # description
      '#+\\1@#\n',    # end of header
      '.*?',          # solution
      '(?=#+@)',      # beginning of next part
      sep=""
  ),  c(
      '#+@',          # beginning of header
      '(\\d+)',       # beginning of header (?P<part>)
      '#\n',          # beginning of header
      '.*?',          # description
      '#+(\\d+)@#\n', # end of header
      '.*?'           # solution
  ), .source)

  check$initialize(data.frame(
    part = apply(matches, 1, function(match) as.numeric(match[2])),
    solution = apply(matches, 1, function(match) strip(match[6])),
    stringsAsFactors=FALSE
  ))

  problem_match <- regex_break(paste(
    '#+@@#\n', # beginning of header
    '.*?',     # description
    '#+@@#\n', # end of header
    '.*?',     # preamble
    '(?=#+@)', # beginning of first part
    sep = ""
  ), c(
    '#+@@#\n', # beginning of header
    '.*?',     # description
    '#+@@#\n', # end of header
    '.*?'      # preamble
    ), .source)

  if(length(problem_match) == 0)
    stop("NAPAKA: datoteka ni pravilno oblikovana")

  .preamble <- strip(problem_match[1, 4])

  {% for part in parts %}
  if (check$part()) {
    {{ part.validation|indent:"    "|safe }}
  }
  {% endfor %}

  check$summarize()
  {% if authenticated %}
  cat('Shranjujem rešitve na strežnik...\n')
  post <- list(
    data = '{{ data|safe }}',
    signature = '{{ signature }}',
    preamble = .preamble,
    attempts = check$parts,
    source = .source
  )
  response <- postToHost('{{ request.META.SERVER_NAME }}', '{% url upload %}', post, port={{ request.META.SERVER_PORT }})
  cat(response)
  {% else %}
  cat('Rešujete kot anonimni uporabnik, zato rešitve niso shranjene.')
  {% endif %}
}

.check()
