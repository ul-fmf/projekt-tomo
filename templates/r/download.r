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

path <- Find(Negate(is.null), Map(function(f) { f$ofile }, sys.frames()), right=TRUE)
split <- function() {
toJSON <- function( x )
{
  #convert factors to characters
    if( is.factor( x ) == TRUE ) {
        tmp_names <- names( x )
        x = as.character( x )
        names( x ) <- tmp_names
    }

    if( !is.vector(x) && !is.null(x) && !is.list(x) ) {
        x <- as.list( x )
        warning("JSON only supports vectors and lists - But I'll try anyways")
    }

    if( is.null(x) )
        return( "null" )

    #treat named vectors as lists
    if( is.null( names( x ) ) == FALSE ) {
        x <- as.list( x )
    }

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

    if( is.nan(x) )
        return( "\"NaN\"" )

    if( is.na(x) )
        return( "\"NA\"" )

    if( is.infinite(x) )
        return( ifelse( x == Inf, "\"Inf\"", "\"-Inf\"" ) )

    if( is.logical(x) )
        return( ifelse(x, "true", "false") )

    if( is.character(x) )
        return( gsub("\\/", "\\\\/", deparse(x)) )

    if( is.numeric(x) )
        return( as.character(x) )

    stop( "shouldnt make it here - unhandled type not caught" )
}
postToHost <- function(host, path, data.to.send, referer, port=80, ua, accept,
  accept.language, accept.encoding, accept.charset, contenttype, cookie)
{
    if(missing(path))
        path <- "/"
    if(missing(ua))
        ua <- "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.5) Gecko/20070719 Iceweasel/2.0.0.5 (Debian-2.0.0.5-2)"
    if(missing(referer))
        referer <- NULL
    if(missing(accept))
        accept <- "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"
    if(missing(accept.language))
        accept.language <- "de,de-de;q=0.8,en-us;q=0.5,en;q=0.3"
    if(missing(accept.encoding))
        accept.encoding <- "gzip,deflate"
    if(missing(accept.charset))
        accept.charset <- "ISO-8859-1,utf-8;q=0.7,*;q=0.7"
    if(missing(contenttype))
        contenttype <- "application/octet-stream"
    if(missing(cookie))
        cookie <- NULL
    if(missing(data.to.send))
        stop("No data to send provided")
    if(!inherits(data.to.send,"list"))
        stop("Data to send have to be a list")

    dc <- 0; #counter for strings
    #make border
    xx <- as.integer(runif(29, min=0, max=9))
    bo <- paste(xx, collapse="")
    bo <- paste(paste(rep("-", 29), collapse=""), bo, sep="")

    header <- NULL
    header <- c(header,paste("POST ", path, " HTTP/1.1\r\n", sep=""))
    if (port==80)
        header <- c(header,paste("Host: ", host, "\r\n", sep=""))
    else
        header <- c(header,paste("Host: ", host, ":", port,
            "\r\n", sep=""))
    header <- c(header,paste("User-Agent: ", ua, "\r\n", sep=""))
    header <- c(header,paste("Accept: ", accept, "\r\n", sep=""))
    header <- c(header,paste("Accept-Language: ", accept.language,
        "\r\n", sep=""))
    header <- c(header,paste("Accept-Encoding: ", accept.encoding,
        "\r\n", sep=""))
    header <- c(header,paste("Accept-Charset: ", accept.charset,
        "\r\n", sep=""))

    header <- c(header,"Connection: close\r\n")
    if (!is.null(referer))
        header <- c(header,paste("Referer: ", referer, "\r\n", sep=""))
    if (!is.null(cookie))
        header <- c(header,paste("Cookie: ", cookie, "\r\n", sep=""))
    header <- c(header,paste("Content-Type: multipart/form-data; boundary=",substring(bo,3),"\r\n",sep=""))

    mcontent <- NULL # keeps the content.

    for(x in 1:length(data.to.send)) {
        val <- data.to.send[[x]]
        key <- names(data.to.send)[x]
        if (typeof(val)=="list") {
            ds <- c(charToRaw(sprintf("%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\nContent-Type: %s\r\n\r\n", bo, key, val$filename, contenttype)), val$object, charToRaw("\r\n"))
        } else {
            ds <- charToRaw(sprintf("%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n", bo,as.character(key),as.character(val)))
        }
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
source <- paste(readLines(path), collapse="\n")
  header_pattern <- paste(
    '(?sm)',          # dot-all and multi-line
    '#{50,}@(\\d+)#', # beginning of header
    '.*',             # header
    '#{50,}\\1@#',    # end of header
    sep=""
  )
  attempt_pattern <- paste(
    header_pattern,  # header
    '.*?',           # solution
    '(?=#{50,}@)',   # beginning of next part
    sep=""
  )
  matches <- gregexpr(attempt_pattern, source, perl=TRUE)[[1]]
  matches <- mapply(function(start, end) {substr(source, start, end)}, matches, matches + attr(matches, "match.length") - 1)
  extract_solution <- function(match) {
    solution <- sub(header_pattern, replacement='', match, perl=TRUE)
    solution <- gsub("^\\s+|\\s+$", "", solution)
    solution
  }
  extract_part <- function(match) {
    part_match <- gregexpr('(?<=@)\\d+(?=#\n)', match, perl=TRUE)[[1]]
    part <- as.numeric(substr(match, part_match, part_match + attr(part_match, "match.length") - 1))
    part
  }
  attempts <- data.frame(
    part=sapply(matches, extract_part),
    solution=sapply(matches, extract_solution),
    challenge='',
    row.names=1:length(matches),
    stringsAsFactors=FALSE
  )
  for (solution in attempts$solution) {
    eval(parse(text=solution))
  }
  attempts$errors <- list(list())
  current_part <- 0
  part <- function() {
    current_part <<- current_part + 1
    nchar(attempts$solution[current_part]) > 0
  }
  check_equal <- function(example, expected) {
    example <- substitute(example)
    answer <- try(eval(example), silent = TRUE)
    if(!isTRUE(all.equal(answer, expected, check.attributes = FALSE))) {
      error <- paste("Ukaz ", deparse(example), " vrne ", answer, " namesto ", expected, ".", sep="")
      attempts$errors[[current_part]] <<- c(attempts$errors[[current_part]], error)
    }
  }
  check_challenge <- function(x) {
      attempts$challenge[current_part] <<- paste(attempts$challenge[current_part], as.character(x), sep="")
  }
  {% for part in parts %}
    if (part()) {
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
  response <- postToHost('127.0.0.1', '/problem/upload/', data, port=8000)
  response <- sub('.*charset=utf-8', replacement='', response)
  response <- gsub("^\\s+|\\s+$", "", response)
  cat(response)
    {% else %}
    cat('Rešujete kot anonimni uporabnik, zato rešitve niso shranjene.')
    {% endif %}
}
split()
