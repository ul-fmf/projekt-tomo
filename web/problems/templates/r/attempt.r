# =============================================================================
# {{ problem.title|safe }}{% if problem.description %}
#
# {{ problem.description|indent:"# "|safe }}{% endif %}{% for part, solution_attempt in parts %}
# =====================================================================@{{ part.id|stringformat:'06d'}}=
# {{ forloop.counter }}. podnaloga
# {{ part.description|indent:"# "|safe }}
# =============================================================================
{{ solution_attempt|safe }}{% endfor %}








































































































#######################################################################@@#
# Kode pod to črto nikakor ne spreminjajte.
##########################################################################

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

  check$initialize(
    apply(matches, 1, function(match) list(
        part = as.numeric(match[2]),
        solution = match[6]
      )
    )
  )
  check$parts[[length(check$parts)]]$solution = rstrip(check$parts[[length(check$parts)]]$solution)

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

  .preamble <- problem_match[1, 4]

  {% for part, _ in parts %}
  if (check$part()) {
    tryCatch({
      {{ part.validation|indent:"      "|safe }}
    },
    error = function(e) {
      check$error("Testi v izrazu %s sprožijo izjemo %s", deparse(e$call), e$message)
    })
  }
  {% endfor %}

  cat('Shranjujem rešitve na strežnik... ')
  post <- list(
    data = '{{ data|safe }}',
    signature = '{{ signature }}',
    preamble = .preamble,
    attempts = check$parts,
    source = "" # sending source somehow causes problems on the server side.
  )
  tryCatch({
    r <- postJSON(path='{{ submission_url }}', token='{{ authentication_token }}', json=enc2utf8(toJSON(post)))
    response <- fromJSON(r, method = "R")
    cat('Rešitve so shranjene.\n')
    for(rejected in response$rejected)
      check$parts[[as.integer(rejected[[1]])]]$rejection <- rejected[[2]]
    check$summarize()
    if("update" %in% names(response)) {
      cat("Posodabljam datoteko... ")
      index <- 1
      while(file.exists(paste(.filename, ".", index, sep = "")))
        index <- index + 1
      backup.filename = paste(.filename, ".", index, sep = "")
      file.copy(.filename, backup.filename)
      r <- readLines(response$update, encoding="UTF-8", warn=FALSE)
      f <- file(.filename, encoding="UTF-8")
      writeLines(r, f)
      close.connection(f)
      cat("Stara datoteka je preimenovana v ", basename(backup.filename), ".\n", sep = "")
      cat("Če se datoteka v urejevalniku ni osvežila, jo shranite ter ponovno zaženite.\n")
    }
  },
  error = function(r) {
    cat('Pri shranjevanju je prišlo do napake.\n')
    check$summarize()
    cat('Pri shranjevanju je prišlo do napake. Poskusite znova.\n')
  })
}

.check()
