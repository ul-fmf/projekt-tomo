{% load i18n %}{% include 'r/filename.r' %}
.source <- paste(readLines(.filename, encoding = "UTF-8"), collapse="\n")
eval(parse(text = substr(.source, gregexpr(paste0("# =L=I=B=", "R=A=R=Y=@="), .source)[[1]], nchar(.source))))
.problem <- .extract.problem()

# ========================================================================
# {{ problem.title }} {% if problem.description %}
#
# {{ problem.description|indent:"# "|safe }}{% endif %}{% for part in problem.parts.all %}
# ================================================================@{{ part.id|stringformat:'06d'}}=
# {{ part.description|indent:"# "|safe }}{% if part.template %}
# ------------------------------------------------------------------------
# {{ part.template|indent:"# "|safe }}{% endif %}
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
# check$secret({% trans "multiply" %}(100, 100))
# check$secret({% trans "multiply" %}(500, 123))


# ======================================================================@=
# {% trans "Do not change this line or anything below it." %}
# ========================================================================


.validate.current.file()

# =L=I=B=R=A=R=Y=@=

{% include 'r/library.r' %}
{% include 'r/check.r' %}
check$challenge.used <- FALSE
check$challenge <- function(x, hint = "") {
  check$challenge.used <<- TRUE
  check$secret(x, hint)
}

.extract.problem <- function() {
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
      '(^#( [^\n]*)?\n)*?',    # description
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

    return(list(
      title = strip(problem_match[1, 3]),
      description = super_strip(problem_match[1, 5]),
      id = {{ problem.id }},
      problem_set = {{ problem.problem_set.id }}
    ))
}

.validate.current.file <- function() {
    check$summarize()
    if(check$challenge.used) {
      cat('{% trans "Function check$challenge is deprecated. Use check$secret instead." %}\n')
    }
    if(all(sapply(check$parts, function(part) part$valid))) {
      cat('{% trans "The problem is correctly formulated." %}\n')
      if(readline('{% trans "Should I save it on the server [yes/NO]" %}') == '{% trans "yes" %}') {
        cat('{% trans "Saving problem to the server" %}...\n')
        check$parts <<- lapply(check$parts, function(part) {
          part$secret <- lapply(part$secret, function(secret) secret[1])
          part
        })
        .problem$parts <<- check$parts
        r <- POST(
          '{{ submission_url }}',
          body = .problem,
          encode = "json",
          add_headers(Authorization = 'Token {{ authentication_token }}')
        )
        response <- content(r)
        if (is.atomic(response)) {
          cat(response, "\n")
        } else if("update" %in% names(response)) {
          file.copy(.filename, paste(.filename, ".orig", sep=""))
          f <- file(.filename, encoding="UTF-8")
          writeLines(response$update, f)
          close.connection(f)
        }
      } else {
        cat('{% trans "Problem was not saved." %}\n')
      }
    } else {
      cat('{% trans "The problem is not correctly formulated." %}\n')
    }
}
