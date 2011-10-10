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
toJSON <- function( x )
{
    #named lists only
    if( is.list(x) && !is.null(names(x)) ) {
        if( any(duplicated(names(x))) )
            stop( "A JSON list must have unique names" );
        str = "{"
        first_elem = TRUE
        for( n in names(x) ) {
            if( first_elem )
                first_elem = FALSE
            else
                str = paste(str, ',', sep="")
            str = paste(str, deparse(n), ":", toJSON(x[[n]]), sep="")
        }
        str = paste( str, "}", sep="" )
        return( str )
    }

    #treat lists without names as JSON array
    if( length(x) != 1 || is.list(x) ) {
        if( !is.null(names(x)) )
            return( toJSON(as.list(x)) ) #vector with names - treat as JSON list
        str = "["
        first_elem = TRUE
        for( val in x ) {
            if( first_elem )
                first_elem = FALSE
            else
                str = paste(str, ',', sep="")
            str = paste(str, toJSON(val), sep="")
        }
        str = paste( str, "]", sep="" )
        return( str )
    }

    if( is.character(x) )
        return( gsub("\\/", "\\\\/", deparse(x)) )

    if( is.numeric(x) )
        return( as.character(x) )

    stop( "shouldnt make it here - unhandled type not caught" )
}
postToHost <- function(host, path, data.to.send, referer, port=80, ua, accept,
  accept.language, accept.encoding, accept.charset, contenttype, cookie)
{
    host <- host
    port <- port
    path <- path

    dc <- 0; #counter for strings
    #make border
    xx <- as.integer(runif(29, min=0, max=9))
    bo <- paste(xx, collapse="")
    bo <- paste(paste(rep("-", 29), collapse=""), bo, sep="")

    header <- NULL
    header <- c(header,paste("POST ", path, " HTTP/1.1\r\n", sep=""))
    header <- c(header,paste("Host: ", host, ":", port, "\r\n", sep=""))
    header <- c(header,"Connection: close\r\n")
    header <- c(header,paste("Content-Type: multipart/form-data; boundary=",substring(bo,3),"\r\n",sep=""))

    mcontent <- NULL # keeps the content.

    for(x in 1:length(data.to.send)) {
        val <- data.to.send[[x]]
        key <- names(data.to.send)[x]
        ds <- charToRaw(sprintf("%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n", bo,as.character(key),as.character(val)))
        dc <- dc + length(ds)
        mcontent <- c(mcontent,ds)
    }

    dc <- dc + length(strsplit(bo,"")[[1]])+4;
    header <- c(header,paste("Content-Length: ",dc,"\r\n\r\n",sep=""))
    mypost <- c(charToRaw(paste(header, collapse="")),mcontent,
        charToRaw(paste(bo,"--\r\n",sep="")))
    rm(header,mcontent)

    scon <- socketConnection(host=host,port=port,open="a+b",blocking=TRUE)
    writeBin(mypost, scon, size=1)

    output <- character(0)
    #start <- proc.time()[3]
    repeat{
        ss <- rawToChar(readBin(scon, "raw", 2048))
        output <- paste(output,ss,sep="")
        if(regexpr("\r\n0\r\n\r\n",ss)>-1) break()
        if(ss == "") break()
        #if(proc.time()[3] > start+timeout) break()
    }
    close(scon)
    return(output)
}
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
    for (solution in attempts$solution) {
        eval(parse(text=solution))
    }
    attempts$errors <- list(list())
    check <- list()
    check$current_part <- 0
    check$part <- function() {
      check$current_part <<- check$current_part + 1
      nchar(attempts$solution[check$current_part]) > 0
    }
    check$equal <- function(example, expected) {
      example <- substitute(example)
      answer <- try(eval(example), silent = TRUE)
      if(!isTRUE(all.equal(answer, expected, check.attributes = FALSE))) {
        error <- paste("Ukaz ", deparse(example), " vrne ", answer, " namesto ", expected, ".", sep="")
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
