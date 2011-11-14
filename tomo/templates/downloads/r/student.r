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




























































get_current_filename <- function () {
  if (length(showConnections()) > 1) {
    return(showConnections()[1, "description"])
  } else {
    return(Find(Negate(is.null), Map(function(f) { f$ofile }, sys.frames()), right=TRUE))
  }
}
.filename <- get_current_filename()

.check <- function() {
  {% include 'downloads/r/rjson.r' %}
  {% include 'downloads/r/library.r' %}
  {% include 'downloads/r/check.r' %}

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

  check$initialize(
    apply(matches, 1, function(match) list(
        part = as.numeric(match[2]),
        solution = strip(match[6])
      )
    )
  )

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
    source = "" # sending source somehow causes problems on the server side.
  )
  tryCatch({
    r <- postJSON(host='{{ request.META.SERVER_NAME }}', path='{% url student_upload %}', port={{ request.META.SERVER_PORT }}, json=toJSON(post))
    response <- fromJSON(r, method = "R")
    for(judgment in response$judgments) {
      print(judgment)
    }
    if(response$outdated) {
      cat("Na voljo je nova različica.")
      index <- 1
      while(file.exists(paste(.filename, ".", index, sep = "")))
        index <- index + 1
      backup.filename = paste(.filename, ".", index, sep = "")
      cat("Trenutno datoteko kopiram v ", backup.filename, ".", sep = "")
      file.copy(.filename, backup.filename)
      r <- postJSON(host='{{ request.META.SERVER_NAME }}', path='{% url api_student_contents %}', port={{ request.META.SERVER_PORT }}, json=toJSON(post))
      cat(r, file=.filename)
    }
  },
  error = function(r) {
    cat('Pri shranjevanju je prišlo do napake. Poskusite znova.')
  })
  {% else %}
  cat('Rešujete kot anonimni uporabnik, zato rešitve niso shranjene.')
  {% endif %}
}

.check()
