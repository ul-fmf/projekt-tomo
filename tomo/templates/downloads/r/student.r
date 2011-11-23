{% load my_tags %}#####################################################################@@#
# {{ problem.title }} {% if problem.description %}
#
# {{ problem.description|remove_markdown|safe }}{% endif %}
#####################################################################@@#

{{ preamble|safe }}

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
  cat('Shranjujem rešitve na strežnik... ')
  post <- list(
    data = '{{ data|safe }}',
    signature = '{{ signature }}',
    preamble = .preamble,
    attempts = check$parts,
    source = "" # sending source somehow causes problems on the server side.
  )
  tryCatch({
    r <- postJSON(host='{{ request.META.SERVER_NAME }}', path='{% url student_upload %}', port={{ request.META.SERVER_PORT }}, json=enc2utf8(toJSON(post)))
    response <- fromJSON(r, method = "R")
    cat('Rešitve so shranjene.\n')
    for(rejected in response$rejected)
      cat("Rešitev podnaloge ", rejected[[1]], " je zavrnjena (", rejected[[2]], ").\n", sep = "")
    if("update" %in% names(response)) {
      cat("Na voljo je nova različica... Posodabljam datoteko... ")
      index <- 1
      while(file.exists(paste(.filename, ".", index, sep = "")))
        index <- index + 1
      backup.filename = paste(.filename, ".", index, sep = "")
      file.copy(.filename, backup.filename)
      r <- readLines(response$update, encoding="UTF-8", warn=FALSE)
      f <- file(.filename, encoding="UTF-8")
      writeLines(r, f)
      close.connection(f)
      cat("Datoteka je posodobljena.\n")
      cat("Kopija stare datoteke je v ", backup.filename, ".\n", sep = "")
      cat("Če se datoteka v urejevalniku ni osvežila, jo shranite ter ponovno zaženite.")
    }
  },
  error = function(r) {
    cat('Pri shranjevanju je prišlo do napake. Poskusite znova.')
    check$error = r$message
  })
  {% else %}
  cat('Naloge rešujete kot anonimni uporabnik, zato rešitve niso shranjene.\n')
  {% endif %}
}

.check()
