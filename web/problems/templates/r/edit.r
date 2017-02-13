{% load i18n %}##########################################################################
# To je datoteka, s katero pripravite nalogo.
# Vsebina naloge je spodaj, za vsemi pomožnimi definicijami.
##########################################################################
{% include 'r/rjson.r' %}
{% include 'r/library.r' %}
{% include 'r/check.r' %}

.filename <- get_current_filename()
.source <- paste(readLines(.filename, encoding = "UTF-8"), collapse="\n")

matches <- regex_break(paste(
  '^#+@(\\d+)#\n',         # beginning of header
  '(^#( [^\n]*)?\n)*',     # description
  '^#+\\1@#\n',            # end of header
  '.*?',                   # solution
  '^check\\$part\\(\\)\n', # beginning of validation
  '.*?',                   # validation
  '^(# )?(?=#+@)',         # beginning of next part
  sep=""
), c(
  '^#+@',                  # beginning of header
  '(\\d+)',                # beginning of header (?P<part>)
  '#\n',                   # beginning of header
  '(^#( [^\n]*)?\n)*',     # description
  '^#+(\\d+)@#\n',         # end of header
  '.*?',                   # solution
  'check\\$part\\(\\)\n',  # beginning of validation
  '.*?',                   # validation
  '^(# )?'                 # beginning of next part
), .source)

  check$initialize(
    apply(matches, 1, function(match) list(
        part = as.numeric(match[2]),
        description = super_strip(match[4]),
        solution = strip(match[6]),
        template = '',
        validation = strip(match[8]),
        problem = {{ problem.id }}
      )
    )
  )


problem_match <- regex_break(paste(
  '^#+@@#\n',          # beginning of header
  '^# ([^\n]*)\n',     # title
  '^(#\\s*\n)*',       # empty rows
  '(^#( [^\n]*)?\n)*', # description
  '^#+@@#\n',          # end of header
  '.*?',               # preamble
  '^(# )?(?=#+@)',     # beginning of first part
  sep = ""
), c(
  '^#+@@#\n',          # beginning of header
  '^# ',               # title
  '([^\n]*)',          # title (?P<title>)
  '\n^(#\\s*\n)*',     # title & empty rows
  '(^#( [^\n]*)?\n)*', # description
  '^#+@@#\n',          # end of header
  '.*?'                # preamble
  ), .source)

if(length(problem_match) == 0)
  stop("NAPAKA: datoteka ni pravilno oblikovana")

title <- strip(problem_match[1, 3])
description <- super_strip(problem_match[1, 5])
preamble <- strip(problem_match[1, 7])

##########################################################################
# Od tu naprej je navodilo naloge

#######################################################################@@#
# {{ problem.title }} {% if problem.description %}
#
# {{ problem.description|indent:"# "|safe }}{% endif %}
#######################################################################@@#

{{ problem.preamble|safe }}

{% for part in parts %}
##################################################################@{{ part.id|stringformat:'06d'}}#
# {{ part.description|indent:"# "|safe }}
##################################################################{{ part.id|stringformat:'06d'}}@#
{{ part.solution|safe }}

check$part()
{{ part.validation|safe }}

{% endfor %}

# ##################################################################@000000#
# # To je predloga za novo podnalogo. Tu vpisite besedilo podnaloge.
# ##################################################################000000@#
#
# sem napisite resitev
#
# check$part()
#
# check$equal(testni_primer, resitev)
#
# check$challenge(testni_primer_1)
# check$challenge(testni_primer_2)
# check$challenge(testni_primer_3)
# ...

#######################################################################@@#
# Od tu naprej ničesar ne spreminjajte.

check$summarize()
if(any(sapply(check$parts, function(part) length(part$errors) > 0))) {
  cat('{% trans "The problem is not correctly formulated." %}\n')
} else {
  cat('{% trans "The problem is correctly formulated." %}\n')
  if(readline('{% trans "Should I save it on the server [yes/NO]" %}') == '{% trans "yes" %}') {
    cat('{% trans "Saving problem to the server" %}...\n')
    post <- list(
      title = title,
      description = description,
      parts = check$parts,
      id = {{ problem.id }},
      problem_set = {{ problem.problem_set.id }}
    )
    r <- postJSON(path='/api/attempts/submit/', token='{{ authentication_token }}', json=enc2utf8(toJSON(post)))
    response <- fromJSON(r, method = "R")
    cat(response$message, "\n")
    if("update" %in% names(response)) {
      file.copy(.filename, paste(.filename, ".orig", sep=""))
      r <- readLines(response$update, encoding="UTF-8", warn=FALSE)
      f <- file(.filename, encoding="UTF-8")
      writeLines(r, f)
      close.connection(f)
    }
  } else {
    cat('{% trans "Problem was not saved." %}\n')
  }
}
