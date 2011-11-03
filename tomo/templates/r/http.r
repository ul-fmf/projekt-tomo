postToHost <- function(host, path, data.to.send, referer, port=80, ua, accept,
  accept.language, accept.encoding, accept.charset, contenttype, cookie) {
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