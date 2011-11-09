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
  pair <- c(toString(k), toString(check$canonize(x)))
  check$parts$challenge[[check$part.counter]] <<-
    c(check$parts$challenge[[check$part.counter]], list(pair))
}

check$run <- function(example, state) {
  # yet to be implemented
}

check$canonize <- function(x, digits = 6) {
  if(typeof(x) == "double" || typeof(x) == "complex") {
    return(round(x, digits))
  } else if(typeof(x) == "complex") {
    return(round(x, digits))
  } else if(typeof(x) == "list") {
    return(lapply(x, function(y) canonize(y, digits)))
  } else {
    return(x)
  }
}

check$compare <- function(example, expected,
                          message = "Ukaz %s vrne %s namesto %s",
                          clean = NA, digits = 6, precision = 1.0e-6,
                          strict_float = FALSE, strict_list = TRUE) {
  example <- substitute(example)
  answer <- try(eval(example), silent = TRUE)
  if(is.na(clean))
    clean <- function(x) check$canonize(x, digits)
  # give a reason for difference like in check.py
  if(!identical(clean(answer), clean(expected))) {
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
    check$error(sprintf(message, deparse(example),
                pretty.print(answer), pretty.print(expected)))
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

