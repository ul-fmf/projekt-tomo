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
    '#{50,}@',
    '(\\d+)',
    '#.*#{50,}\\1@#', # header
    '.*?', #solution
    '(?=#{50,}@)',   # beginning of next part
    sep=""
), c(
    '#{50,}@',
    '(\\d+)',
    '#',
    '.*?',
    '#{50,}(\\d+)@#', # header
    '.*?', #solution
    'check\\$part\\(\\)',
    '.*?' #validation
), .source)

check$initialize(data.frame(
  part = apply(matches, 1, function(match) as.numeric(match[2])),
  description = apply(matches, 1, function(match) super_strip(match[4])),
  solution = apply(matches, 1, function(match) strip(match[6])),
  validation = apply(matches, 1, function(match) strip(match[8])),
  stringsAsFactors = FALSE
))


problem_match <- regex_breax(
  '#{50,}@@#\n#.*?(?=#{50,}@(\\d+))', c(
  '#{50,}@@#\n#',
  '.*?',
  '\n',
  '.*?',
  '#{50,}@@#', # header
  '.*?' #solution
  ), .source)

if(length(problem_match) == 0)
  stop("NAPAKA: datoteka ni pravilno oblikovana")

title <- strip(problem_match[1, 2])
description <- super_strip(problem_match[1, 4])
preamble <- strip(problem_match[1, 6])

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
if(any(length(check$parts$errors) > 0)) {
  stop('Naloge so napačno sestavljene.')
} else {
  cat('Naloge so pravilno sestavljene.\n')
  cat('Shranjujem naloge...')
  post <- list(
    data = '{{ data|safe }}',
    signature = '{{ signature }}',
    timestamp = '{{ timestamp }}',
    title = title,
    description = description,
    preamble = preamble,
    parts = check$dump()
  )
  response <- postToHost('{{ request.META.SERVER_NAME }}', '{% url update %}', data, port={{ request.META.SERVER_PORT }})
  cat(response)
}
