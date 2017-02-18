{% load i18n %}##########################################################################
# To je datoteka, s katero pripravite nalogo.
# Vsebina naloge je spodaj, za vsemi pomožnimi definicijami.
##########################################################################
{% include 'r/library.r' %}
{% include 'r/check.r' %}

.filename <- get_current_filename()
.source <- paste(readLines(.filename, encoding = "UTF-8"), collapse="\n")

matches <- regex_break(paste(
  '^# ===+@(\\d+)=\n',     # beginning of part header
  '(^#( [^\n]*)?\n)*',     # description
  '(# ---+\n',             # optional beginning of template
  '((#( [^\n]*)?\n)*))?',  # solution template
  '^# =+\\1@=\n',          # end of part header
  '.*?',                   # solution
  '^check\\$part\\(\\)\n', # beginning of validation
  '.*?',                   # validation
  '^(# )?(?=# =+@)',       # beginning of next part
  sep=""
), c(
  '^# ===+@',              # beginning of part header
  '(\\d+)',                # beginning of part header (?P<part>)
  '=\n',                   # beginning of part header
  '(^#( [^\n]*)?\n)*',     # description
  '(# ---+\n((#( [^\n]*)?\n)*))?',  # solution template
  '^# =+(\\d+)@=\n',       # end of part header
  '.*?',                   # solution
  'check\\$part\\(\\)\n',  # beginning of validation
  '.*?',                   # validation
  '^(# )?'                 # beginning of next part
), .source)

  check$initialize(
    apply(matches, 1, function(match) list(
        part = as.numeric(match[2]),
        description = super_strip(match[4]),
        solution = strip(match[7]),
        template = super_strip(gsub("^[^\n]+\n", "", match[5])),
        validation = strip(match[9]),
        problem = {{ problem.id }}
      )
    )
  )


problem_match <- regex_break(paste(
  '^# =+\n',           # beginning of header
  '^# ([^\n]*)\n',     # title
  '^(#\\s*\n)*',       # empty rows
  '(^#( [^\n]*)?\n)*', # description
  '^(# )?(?==+@)',     # beginning of first part
  sep = ""
), c(
  '^# =+\n',           # beginning of header
  '^# ',               # title
  '([^\n]*)',          # title (?P<title>)
  '\n^(#\\s*\n)*',     # title & empty rows
  '(^#( [^\n]*)?\n)*', # description
  '^(# )?'             # beginning of first part
  ), .source)

if(length(problem_match) == 0)
  stop("NAPAKA: datoteka ni pravilno oblikovana")

title <- strip(problem_match[1, 3])
description <- super_strip(problem_match[1, 5])

##########################################################################
# Od tu naprej je navodilo naloge

# ========================================================================
# {{ problem.title }} {% if problem.description %}
#
# {{ problem.description|indent:"# "|safe }}{% endif %}{% for part in problem.parts.all %}
# ================================================================@{{ part.id|stringformat:'06d'}}=
# {{ part.description|indent:"# "|safe }}
# ================================================================{{ part.id|stringformat:'06d'}}@=
{{ part.solution|safe }}

check$part()
{{ part.validation|safe }}

{% endfor %}

# # ================================================================@000000=
# # {% blocktrans %}This is a template for a new problem part. To create a new part, uncomment
# # the template and fill in your content.
# # Define a function `multiply(x, y)` that returns the product of `x` and `y`.
# # For example:
# #
# #     > multiply(3, 7)
# #     21
# #     > multiply(6, 7)
# #     42{% endblocktrans %}
# # ================================================================000000@=
#
# {% trans "multiply" %} <- function(x, y) x * y
#
# check$part()
#
# check$equal({% trans "multiply" %}(3, 7), 21)
# check$equal({% trans "multiply" %}(6, 7), 42)
# check$equal({% trans "multiply" %}(10, 10), 100)
# check$challenge({% trans "multiply" %}(100, 100))
# check$challenge({% trans "multiply" %}(500, 123))

# =====================================================================@@=
# {% trans "Do not change this line or anything below it." %}

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
    r <- POST(
      '{{ submission_url }}',
      body = post,
      encode = "json",
      add_headers(Authorization = 'Token {{ authentication_token }}')
    )
    response <- content(r)
    cat(response$message, "\n")
    if("update" %in% names(response)) {
      file.copy(.filename, paste(.filename, ".orig", sep=""))
      f <- file(.filename, encoding="UTF-8")
      writeLines(response$update, f)
      close.connection(f)
    }
  } else {
    cat('{% trans "Problem was not saved." %}\n')
  }
}
