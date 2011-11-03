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
