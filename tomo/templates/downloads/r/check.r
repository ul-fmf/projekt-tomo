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
  return(check$parts[[check$part.counter]]$solution != "")
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
    return(lapply(x, function(y) canonize(y, digits)))
  } else {
    return(x)
  }
}

check$equal <- function(example, expected,
                          message = "Ukaz %s vrne %s namesto %s (%s)",
                          clean = function(x) x, digits = 6, precision = 1.0e-6,
                          strict_float = FALSE, strict_list = TRUE) {
  difference <- function(x, y) {
    if(identical(x, y)) return(NA)
    else if(typeof(x) != typeof(y) && (strict_float || !(mode(x) != mode(y))))
      return("različna tipa")
    else if(!is.null(dim(y))) {
      if(dim(x) != dim(y)) return("različne dimenzije")
    }
    else if(mode(y) == 'numeric') {
      if(any(abs(x - y) > precision))
        return("numerična napaka")
      else
        return(NA)
    }
    else if(!isTRUE(attr.all.equal(x, y))) {
      return("različne lastnosti")
    }
    else return("različni vrednosti")
    return(!isTRUE(all.equal(x, y, check.attributes = FALSE)))
  }
  example <- substitute(example)
  answer <- try(eval(example), silent = TRUE)
  reason <- difference(clean(answer), clean(expected))
  if(!is.na(reason)) {
    pretty.print <- function(x) {
      output <- capture.output(
        if(length(dim(x)) <= 1) cat(x) else print(x)
      )
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

check$summarize <- function() {
  for(i in 1:length(check$parts)) {
    if(check$parts[[i]]$solution == "") {
      cat("Podnaloga", i, "je brez rešitve.\n")
    } else if (length(check$parts[[i]]$errors) > 0) {
      cat("Podnaloga", i, "ni prestala vseh testov.\n")
      cat(paste("- ", check$parts[[i]]$errors, "\n", sep = ""), sep = "")
    } else {
      cat("Podnaloga", i, "je prestala vse teste.\n")
    }
  }
}
