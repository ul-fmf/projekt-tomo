check$part <- function() {
  check$current_part <<- check$current_part + 1
  solution <- attempts$solution[check$current_part]
  eval(parse(text=solution))
  return(nchar(solution) > 0)
}
check$equal <- function(example, expected) {
  example <- substitute(example)
  answer <- try(eval(example), silent = TRUE)
  if(!isTRUE(all.equal(answer, expected, check.attributes = FALSE))) {
    error <- paste("Ukaz ", deparse(example), " vrne ", toString(answer), " namesto ", toString(expected), ".", sep="")
    attempts$errors[[check$current_part]] <<- c(attempts$errors[[check$current_part]], error)
  }
}
check$challenge <- function(x) {
  attempts$challenge[check$current_part] <<- paste(attempts$challenge[check$current_part], as.character(x), sep="")
}