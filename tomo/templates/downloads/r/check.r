check <- list()

check$initialize <- function(parts) {
  init.part <- function(part) {
    part$errors <- list()
    part$challenge <- list()
    return(part)
  }
  check$parts <<- lapply(parts, init.part)
  check$current <<- NA
  check$part.counter <<- NA
}

check$part <- function() {
  if(is.na(check$part.counter)) {
    check$part.counter <<- 1
  } else {
    check$part.counter <<- check$part.counter + 1
  }
  return(strip(check$parts[[check$part.counter]]$solution) != "")
}

check$error <- function(msg) {
  check$parts[[check$part.counter]]$errors <<-
    c(check$parts[[check$part.counter]]$errors, msg)
}

check$challenge <- function(x, k = NA) {
  pair <- c(toString(k), toString(check$canonize(x)))
  check$parts[[check$part.counter]]$challenge<<-
    c(check$parts[[check$part.counter]]$challenge, list(pair))
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
    return(lapply(x, function(y) check$canonize(y, digits)))
  } else {
    return(x)
  }
}

check$equal <- function(example, expected,
                          message = "Ukaz %s vrne %s namesto %s (%s)",
                          clean = function(x) x, digits = 6, precision = 1.0e-6,
                          strict.float = FALSE, check.attributes = FALSE) {
  difference <- function(x, y) {
    if(identical(x, y)) return(NA)
    else if(isTRUE(all.equal(x, y, check.attributes = check.attributes))) return(NA)
    else if(typeof(x) != typeof(y) && (strict.float || !(mode(x) != mode(y))))
      return("različna tipa")
    else if(length(x) != length(y))
      return("različno število komponent")
    else if(mode(y) == 'numeric') {
      if(any(abs(x - y) > precision))
        return("numerična napaka")
      else
        return(NA)
    }
    else return("različni vrednosti")
  }
  example <- substitute(example)
  answer <- try(eval(example), silent = TRUE)
  reason <- difference(clean(answer), clean(expected))
  if(!is.na(reason)) {
    pretty.print <- function(x) {
      output <- capture.output(print(x))
      if(length(output) == 0) {
        return("NULL")
      } else if(length(output) == 1) {
        return(output)
      } else {
        return(paste("    ", c("", output, ""), collapse = "\n"))
      }
    }
    check$error(sprintf(message, deparse(example),
                pretty.print(answer), pretty.print(expected), reason))
  }
}

check$equal.error <- function(example, expected) {
  example = substitute(example)
  no.error <- TRUE
  tryCatch(
    eval(example),
    error = function(e) {
      no.error <<- FALSE
      if(e$message != expected) {
        check$error(sprintf("Izraz %s sproži napako \'%s\' in ne \'%s\'",
                            deparse(example), e$message, expected))
      }
    }
  )
  if(no.error) {
        check$error(sprintf("Izraz %s vrne vrednost namesto da bi sprožil napako \'%s\'",
                            deparse(example), expected))
  }
}

check$summarize <- function() {
  for(i in 1:length(check$parts)) {
    if(strip(check$parts[[i]]$solution) == "") {
      cat("Podnaloga", i, "je brez rešitve.\n")
    } else if (length(check$parts[[i]]$errors) > 0) {
      cat("Podnaloga", i, "ni prestala vseh testov.\n")
      cat(paste("- ", check$parts[[i]]$errors, "\n", sep = ""), sep = "")
    } else {
      cat("Podnaloga", i, "je prestala vse teste.\n")
    }
  }
}
