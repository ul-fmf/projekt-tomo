{% load my_tags %}

if (length(showConnections()) > 1) {
    path <- showConnections()[1, "description"]
} else {
    path <- Find(Negate(is.null), Map(function(f) { f$ofile }, sys.frames()), right=TRUE)
}
split <- function() {

    # Auxillary functions
    # extract solutions
    # perform tests
    # prepare json
    # submit data
    # print result
    {% include 'r/json.r' %}
    {% include 'r/http.r' %}
regex_break <- function(whole_regex, regexes, source) {
    whole_matches <- gregexpr(paste("(?sm)", whole_regex, sep=""), source, perl=TRUE)[[1]]
    whole_matches <- mapply(
        function(start, end) substr(source, start, end),
        whole_matches,
        whole_matches + attr(whole_matches, "match.length") - 1
    )
    m <- length(whole_matches)
    n <- length(regexes)
    matches <- matrix("", nrow=m, ncol=n)
    for (i in 1:m) {
        whole <- whole_matches[i]
        for (j in 1:length(regexes)) {
            rest_regex <- paste(regexes[-(1 : j)], collapse="")
            part_regex <- paste("(?sm)\\A", regexes[j], "(?=", rest_regex, "\\Z)", sep="")
            match <- regexpr(part_regex, whole, perl=TRUE)
            end <- attr(match, "match.length")
            matches[i, j] <- substr(whole, 1, end)
            whole <- substr(whole, end + 1, nchar(whole))
        }
    }
    matches
}
    source <- paste(readLines(path), collapse="\n")
    problem_regex <- c(
        '#{50,}@@#\n#',
        '.*?',
        '\n',
        '.*?',
        '#{50,}@@#', # header
        '.*?' #solution
    )
    trim <- function(str) gsub("^\\s+|\\s+$", "", str)
    super_trim <- function(str) {
        str <- gsub("(^|\n)# ?", "\n", str)
        str <- gsub("\\A\\s+|\\s+\\Z", "", str, perl=TRUE)
    }
    problem_match <- regex_break('#{50,}@@#\n#.*?(?=#{50,}@(\\d+))', problem_regex, source)
    title <- trim(problem_match[1, 2])
    description <- super_trim(problem_match[1, 4])
    preamble <- trim(problem_match[1, 6])
    whole_regex <- paste(
        '#{50,}@',
        '(\\d+)',
        '#.*#{50,}\\1@#', # header
        '.*?', #solution
        '(?=#{50,}@)',   # beginning of next part
        sep=""
    )
    regexes <- c(
        '#{50,}@',
        '(\\d+)',
        '#',
        '.*?',
        '#{50,}(\\d+)@#', # header
        '.*?', #solution
        'check\\$part\\(\\)',
        '.*?' #validation
    )
    matches <- regex_break(whole_regex, regexes, source)
    parts <- data.frame(
      part=apply(matches, 1, function(match) as.numeric(match[2])),
      description=apply(matches, 1, function(match) super_trim(match[4])),
      solution=apply(matches, 1, function(match) trim(match[6])),
      validation=apply(matches, 1, function(match) trim(match[8])),
      challenge='',
      row.names=1:nrow(matches),
      stringsAsFactors=FALSE
    )
    for (solution in parts$solution) {
        eval(parse(text=solution))
    }
    parts$errors <- list(list())
    check <- list()
    check$current_part <- 0


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

#####################################################################@@#
# Kode pod to črto nikakor ne spreminjajte.
########################################################################

invisible("TA VRSTICA JE PRAVILNA.")
"ČE VAM R SPOROČI, DA JE V NJEJ NAPAKA, SE MOTI."
"NAPAKA JE NAJVERJETNEJE V ZADNJI VRSTICI VAŠE KODE."
"ČE JE NE NAJDETE, VPRAŠAJTE ASISTENTA."


  for (i in 1:length(parts$solution)) {
    cat('Naloga ', i, ') je', sep='', end=' ')
    if (nchar(parts$solution[i]) == 0) {
      cat('brez rešitve.\n')
    } else if (length(parts$errors[[i]]) > 0) {
      cat('napačno rešena.\n')
      cat(paste('- ', paste(parts$errors[[i]], collapse="\n- "), "\n", sep=""))
    } else {
      cat('pravilno rešena.\n')
    }
  }
  cat('Shranjujem naloge...\n')
  parts <- paste('[', paste(apply(parts, 1, toJSON), collapse=', '), ']',  sep='')
  data <- list(
            parts=parts, source=source,
            data='{{ data|safe }}',
            signature='{{ signature }}',
            title=title, description=description, preamble=preamble
            )
  response <- postToHost('{{ request.META.SERVER_NAME }}', '{% url update %}', data, port={{ request.META.SERVER_PORT }})
  # response <- sub('(?ms).*(?=Shranjeno.)', replacement='', response, perl=TRUE)
  # response <- gsub("^\\s+|(\\s*0\\s*)$", "", response)
  cat(response)
}
split()
