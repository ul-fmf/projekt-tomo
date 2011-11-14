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

strip <- function(str) gsub("^\\s+|\\s+$", "", str)

super_strip <- function(str) {
    str <- gsub("(^|\n)# ?", "\n", str)
    str <- gsub("\\A\\s+|\\s+\\Z", "", str, perl=TRUE)
}

get_current_filename <- function () {
  if (length(showConnections()) > 1) {
    return(showConnections()[1, "description"])
  } else {
    return(Find(Negate(is.null), Map(function(f) { f$ofile }, sys.frames()), right=TRUE))
  }
}

# Code is borrowed from httpRequest package.

postJSON <-function(host, path, port=80, json) {
  fp <- make.socket(host=host, port=port, server=FALSE)
  write.socket(fp, paste(
    "POST ", path, " HTTP/1.1\n",
    "Host: ", host, "\n",
    "Content-Type: application/json; charset=utf-8\n",
    "Content-Length: ", nchar(json, "bytes"), "\n\n",
    json,
    # I HAVE ABSOLUTELY NO IDEA WHY THIS HAS TO BE HERE, BUT SOMEHOW, THE
    # REQUEST LENGTH IS TOO SHORT WITHOUT IT.
    rep("\n", nchar(json, "bytes") - nchar(json)),
    collapse = "", sep = ""
  ))
  output <- character(0)
  repeat {
    ss <- read.socket(fp, loop=FALSE)
    output <- paste(output, ss, sep="")
    if(regexpr("\r\n0\r\n\r\n", ss) > -1)
      break()
    if (ss == "")
      break()
  }
  close.socket(fp)
  return(sub("^.*\r\n\r\n", "", output))
}
