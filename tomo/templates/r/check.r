{% include 'r/rjson.r' %}

check <- list()

check$initialize <- function(parts) {
  check$parts <<- parts
  check$parts$errors <<- list(list())
  check$parts$challenge <<- list(list())
  check$current <<- NA
  check$part.counter <<- NA
}

check$part <- function() {
  if(is.na(check$part.counter)) {
    check$part.counter <<- 1
  } else {
    check$part.counter <<- check$part.counter + 1
  }
  return(check$parts$solution[[check$part.counter]] != "")
}

check$error <- function(msg) {
  check$parts$errors[[check$part.counter]] <<-
    c(check$parts$errors[[check$part.counter]], msg)
}

check$challenge <- function(x, k = NA) {
  pair <- c(toString(k), toString(x))
  check$parts$challenge[[check$part.counter]] <<-
    c(check$parts$challenge[[check$part.counter]], list(pair))
}

check$compare <- function(example, expected) {
  pretty.print <- function(x) {
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
  example <- substitute(example)
  answer <- try(eval(example), silent = TRUE)
  if(!isTRUE(all.equal(answer, expected, check.attributes = FALSE))) {
    check$error(
      paste("Ukaz", deparse(example), "vrne", pretty.print(answer), "namesto", pretty.print(expected))
    )
  }
}

check$summarize <- function() {
  for(i in 1:nrow(check$parts)) {
    if(check$parts$solution[[i]] == "") {
      cat("Podnaloga", i, "je brez rešitve.\n")
    } else if (length(check$parts$errors[[i]]) > 0) {
      cat("Podnaloga", i, "ni prestala vseh testov.\n")
      cat(paste("- ", check$parts$errors[[i]], "\n", sep = ""), sep="")
    } else {
      cat("Podnaloga", i, "je prestala vse teste.\n")
    }
  }
}

check$dump <- function() {
  return(toJSON(check$parts))
}

