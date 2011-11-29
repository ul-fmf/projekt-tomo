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

check$error <- function(msg, ...) {
  check$parts[[check$part.counter]]$errors <<-
    c(check$parts[[check$part.counter]]$errors, sprintf(msg, ...))
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

check$equal <- function(example, value = NA, exception = NA,
                          message = "Ukaz %s vrne %s namesto %s (%s)",
                          clean = function(x) x, precision = 1.0e-6,
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
  raised <- NA
  tryCatch(
    returned <- eval(example),
    error = function(e) {
      raised <<- e$message
      returned <<- NA
    }
  )

  if(!is.na(raised) && is.na(exception)) {
    check$error("Izraz %s bi moral vrniti %s vendar sproži izjemo %s.",
                deparse(example), pretty.print(value), raised)
  } else if(!is.na(raised) && !is.na(exception) && raised != exception) {
    check$error("Izraz %s bi moral sprožiti izjemo %s vendar sproži izjemo %s.",
                deparse(example), exception, raised)

  } else if(!is.na(exception) && is.na(raised)) {
    check$error("Izraz %s bi moral sprožiti izjemo %s vendar vrne %s.",
                deparse(example), exception, pretty.print(returned))

  } else if(is.na(raised) && is.na(exception)) {
    reason <- difference(clean(returned), clean(value))
    if(!is.na(reason)) {
      check$error(message, deparse(example), pretty.print(value),
                  pretty.print(returned), reason)
    }
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
