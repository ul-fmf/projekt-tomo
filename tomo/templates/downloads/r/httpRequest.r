##================================================================
## Simple Post
##================================================================


simplePostToHost<-function(host,path,referer,datatosend,port=80)
  {
    if(!missing(datatosend))
      {
        lengthdatatosend <- nchar(datatosend)
        datatosend <- paste(datatosend,"\n",sep="")
      }
    else
      {
        datatosend<-character(0)
        lengthdatatosend <- 0
      }
    if(missing(path)) path<-"/"
    if(missing(referer)) referer <- ""
    #make the header
    header<-character(0)
    header<-c(header,    paste("POST ",path," HTTP/1.1\n",sep=""))
    header<-c(header,    paste("Host: ",host,"\n",sep=""))
    header<-c(header,    paste("Referer: ",referer,"\n",sep=""))
    header<-c(header,    "Content-Type: application/x-www-form-urlencoded\n")
    # I HAVE NO IDEA WHY SERVER READS TOO LITTLE OF THE DATA TO BE SENT
    header<-c(header,    paste("Content-Length: ",lengthdatatosend+5,"\n"))
    header<-c(header,    "Connection: Keep-Alive\n\n")
    #add the data.
    # HERE WE PAD THE DATA TO BE LONG ENOUGH
    header <- paste(c(header,datatosend,"    "), collapse="")
    ##establish the connection.
    fp <- make.socket(host=host, port=port,server=FALSE)
    write.socket(fp,header)
    output <- character(0)
    #read as long there is nothing more to read.
    repeat
      {
        ss <- read.socket(fp,loop=FALSE)
        output <- paste(output,ss,sep="")
        if(regexpr("\r\n0\r\n\r\n",ss)>-1) break();
        if (ss == "") break();
      }
    close.socket(fp)
    return(output)
  }

