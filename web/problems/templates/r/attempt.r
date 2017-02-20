# ========================================================================
# {{ problem.title }} {% if problem.description %}
#
# {{ problem.description|indent:"# "|safe }}{% endif %}{% for part, solution_attempt in parts %}
# ================================================================@{{ part.id|stringformat:'06d'}}=
# {{ forloop.counter }}. podnaloga
# {{ part.description|indent:"# "|safe }}
# ========================================================================
{{ solution_attempt|safe }}{% endfor %}








































































































# =======================================================================@
# Kode pod to črto nikakor ne spreminjajte.
# ========================================================================

"TA VRSTICA JE PRAVILNA."
"ČE VAM R SPOROČI, DA JE V NJEJ NAPAKA, SE MOTI."
"NAPAKA JE NAJVERJETNEJE V ZADNJI VRSTICI VAŠE KODE."
"ČE JE NE NAJDETE, VPRAŠAJTE ASISTENTA."




























































{% include 'r/filename.r' %}

.check <- function() {
  {% include 'r/library.r' %}
  {% include 'r/check.r' %}

  .source <- paste(readLines(.filename), collapse="\n")

  matches <- regex_break(paste(
      '# =+@(\\d+)=\n',    # beginning of header
      '(#( [^\n]*)?\n)+',  # description
      '# =+\n',            # end of header
      '.*?',               # solution
      '(?=\n# =+@)',       # beginning of next part
      sep=""
  ),  c(
      '# =+@',             # beginning of header
      '(\\d+)',            # beginning of header (?P<part>)
      '=\n',               # beginning of header
      '(#( [^\n]*)?\n)+',  # description
      '# =+\n',            # end of header
      '.*?'                # solution
  ), .source)

  check$initialize(
    apply(matches, 1, function(match) list(
        part = as.numeric(match[2]),
        solution = match[6]
      )
    )
  )
  check$parts[[length(check$parts)]]$solution <- rstrip(check$parts[[length(check$parts)]]$solution)

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
  tryCatch({
    r <- POST(
      '{{ submission_url }}',
      body = check$parts,
      encode = "json",
      add_headers(Authorization = 'Token {{ authentication_token }}')
    )
    response <- content(r)
    cat('Rešitve so shranjene.\n')
    updates <- list()
    for (part in response$attempts) {
      updates[[part$part]] <- part
    }
    for(i in 1:length(check$parts)) {
      valid.before <- check$parts[[i]]$valid
      if (!is.null(updates[[check$parts[[i]]$part]])) {
        for (field in names(updates[[check$parts[[i]]$part]])) {
          check$parts[[i]][[field]] <- updates[[check$parts[[i]]$part]][[field]]
        }
      }
      valid.after <- check$parts[[i]]$valid
      if (valid.before && ! valid.after) {
        wrong.index <- response$wrong_indices[[as.character(check$parts[[i]]$part)]]
        if (! is.null(wrong.index)) {
          hint <- check$parts[[i]]$secret[[wrong.index+1]][2]
          if (nchar(hint) > 0) {
            check$parts[[i]]$feedback <- c(check$parts[[i]]$feedback, paste("Namig:", hint))
          }
        }
      }
    }
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
    check$summarize()
  },
  error = function(r) {
    cat('Pri shranjevanju je prišlo do napake.\n')
    check$summarize()
    cat('Pri shranjevanju je prišlo do napake. Poskusite znova.\n')
  })
}

.check()
