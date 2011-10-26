{% load my_tags %}#####################################################################@@#
# {{ problem.title }} {% if problem.description %}
#
# {{ problem.description|markdown2py|safe }}{% endif %}
#####################################################################@@#

{% for part in parts %}
################################################################@{{ part.id|stringformat:'06d'}}#
# {{ forloop.counter }}) {{ part.description|markdown2py|safe }}
################################################################{{ part.id|stringformat:'06d'}}@#
{% with attempts|get:part.id as attempt %}{% if attempt.solution %}{{ attempt.solution|safe }}{% endif %}{% endwith %}

{% endfor %}






























































#####################################################################@@#
# Kode pod to črto nikakor ne spreminjajte.
########################################################################

invisible("TA VRSTICA JE PRAVILNA.")
"ČE VAM R SPOROČI, DA JE V NJEJ NAPAKA, SE MOTI."
"NAPAKA JE NAJVERJETNEJE V ZADNJI VRSTICI VAŠE KODE."
"ČE JE NE NAJDETE, VPRAŠAJTE ASISTENTA."

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
        '#.*#{50,}(\\d+)@#', # header
        '.*?' #solution
    )
    matches <- regex_break(whole_regex, regexes, source)
    trim <- function(str) gsub("^\\s+|\\s+$", "", str)
    attempts <- data.frame(
      part=apply(matches, 1, function(match) as.numeric(match[2])),
      solution=apply(matches, 1, function(match) trim(match[4])),
      challenge='',
      row.names=1:nrow(matches),
      stringsAsFactors=FALSE
    )
    attempts$errors <- list(list())
    check <- list()
    check$current_part <- 0
    check$part <- function() {
      check$current_part <<- check$current_part + 1
      solution <- attempts$solution[check$current_part]
      eval(parse(text=solution))
      return(nchar(solution) > 0)
    }
    my.print <- function(x) {
      output <- capture.output(
        if(length(dim(x)) <= 1) cat(x) else print(x)
      )
      if(length(output) == 0) {
        return("NULL")
      } else if(length(output) == 1) {
        return(output)
      } else {
        return(paste("    ", c("", output, ""), collapse="\n"))
      }
    }
    check$equal <- function(example, expected) {
      example <- substitute(example)
      answer <- try(eval(example), silent = TRUE)
      if(!isTRUE(all.equal(answer, expected, check.attributes = FALSE))) {
        error <- paste("Ukaz ", deparse(example), " vrne ", my.print(answer), " namesto ", my.print(expected), sep="")
        attempts$errors[[check$current_part]] <<- c(attempts$errors[[check$current_part]], error)
      }
    }
    check$challenge <- function(x) {
      attempts$challenge[check$current_part] <<- paste(attempts$challenge[check$current_part], as.character(x), sep="")
    }
    {% for part in parts %}
    if (check$part()) {
        {{ part.validation|indent:"        "|safe }}
    }
    {% endfor %}

  for (i in 1:length(attempts$solution)) {
    cat('Naloga ', i, ') je', sep='', end=' ')
    if (nchar(attempts$solution[i]) == 0) {
      cat('brez rešitve.\n')
    } else if (length(attempts$errors[[i]]) > 0) {
      cat('napačno rešena.\n')
      cat(paste('- ', paste(attempts$errors[[i]], collapse="\n- "), "\n", sep=""))
    } else {
      cat('pravilno rešena.\n')
    }
  }
{% if authenticated %}
  cat('Shranjujem rešitve...\n')
  attempts <- paste('[', paste(apply(attempts, 1, toJSON), collapse=', '), ']',  sep='')
  data <- list(
            attempts=attempts, source=source,
            data='{{ data|safe }}',
            signature='{{ signature }}'
            )
  response <- postToHost('{{ request.META.SERVER_NAME }}', '{% url upload %}', data, port={{ request.META.SERVER_PORT }})
  response <- sub('(?ms).*(?=Shranjeno.)', replacement='', response, perl=TRUE)
  response <- gsub("^\\s+|(\\s*0\\s*)$", "", response)
  cat(response)
{% else %}
  cat('Rešujete kot anonimni uporabnik, zato rešitve niso shranjene.')
{% endif %}
}
split()
