#################################################################
# To je datoteka, s katero pripravite nalogo.
# Vsebina naloge je spodaj, za vsemi pomožnimi definicijami.
#################################################################
{% load my_tags %}
{% include 'r/httpRequest.r' %}
{% include 'r/rjson.r' %}
{% include 'r/library.r' %}
{% include 'r/check.r' %}

.filename <- get_current_filename()
.source <- paste(readLines(.filename), collapse="\n")

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
  '.*?'                    # validation
), .source)

check$initialize(data.frame(
  part = apply(matches, 1, function(match) as.numeric(match[2])),
  description = apply(matches, 1, function(match) super_strip(match[4])),
  solution = apply(matches, 1, function(match) strip(match[6])),
  validation = apply(matches, 1, function(match) strip(match[8])),
  stringsAsFactors = FALSE
))


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

###################################################################
# Od tu naprej je navodilo naloge

#####################################################################@@#
# {{ problem.title }} {% if problem.description %}
#
# {{ problem.description|indent:"# "|safe }}{% endif %}
#####################################################################@@#

{{ problem.preamble|safe }}

{% for part in parts %}
################################################################@{{ part.id|stringformat:'06d'}}#
# {{ part.description|indent:"# "|safe }}
################################################################{{ part.id|stringformat:'06d'}}@#
{{ part.solution|safe }}

check$part()
{{ part.validation|safe }}

{% endfor %}

# ################################################################@000000#
# # To je predloga za novo podnalogo. Tu vpisite besedilo podnaloge.
# ################################################################000000@#
#
# sem napisite resitev
#
# check$part()
#
# check$compare(...)
#
# check$challenge(...)

#####################################################################@@#
# Od tu naprej ničesar ne spreminjajte.

check$summarize()
if(any(sapply(check$parts$errors, length) > 0)) {
  cat('Naloge so napačno sestavljene.\n')
} else {
  cat('Naloge so pravilno sestavljene.\n')
  if(readline('Ali jih shranim na strežnik? [da/NE]') == 'da') {
    cat('Shranjujem naloge...')
    post <- list(
      data = '{{ data|safe }}',
      signature = '{{ signature }}',
      title = title,
      description = description,
      preamble = preamble,
      parts = check$dump()
    )
    r <- postToHost('{{ request.META.SERVER_NAME }}', '{% url update %}', post, port={{ request.META.SERVER_PORT }})
    response <- parse_response(r)
    cat(response$message, "\n")
    if('contents' %in% names(response)) {
      file.copy(.filename, paste(.filename, ".orig", sep=""))
      cat(response$contents, file=.filename)
    }
  } else {
    cat('Naloge niso bile shranjene.\n')
  }
}
