
library(lattice)
library(reshape)

args <- commandArgs(TRUE)

inSVDPosData <- args[1]
inSVDNegData <- args[2]
inOtherPosData <- args[3]
inOtherNegData <- args[4]
outPlot <- args[5]

# First load the SVD specific data
svdPosData <- read.table(inSVDPosData)
colnames(svdPosData) <- c('idX','idY','score')
svdPosData$class <- "Positive"

svdNegData <- read.table(inSVDNegData)
colnames(svdNegData) <- c('idX','idY','score')
svdNegData$class <- "Negative"


combinedSVDData <- data.frame(class=c(svdNegData$class,svdPosData$class),
                           score=c(svdNegData$score,svdPosData$score))
combinedSVDData$method <- "SVD"


# Then load the other methods data

otherPosData <- read.table(inOtherPosData)
colnames(otherPosData) <- c("idX","idY","factaPlusScore","bitolaScore","anniScore","arrowsmithScore","jaccardScore","preferentialAttachmentScore")
otherPosData$class <- "Positive"
otherPosData <- otherPosData[,3:ncol(otherPosData)]
#otherPosData <- otherPosData[1:1000,]

meltedPosData <- melt(otherPosData,id="class")
colnames(meltedPosData) <- c("class","method","score")

otherNegData <- read.table(inOtherNegData)
colnames(otherNegData) <- c("idX","idY","factaPlusScore","bitolaScore","anniScore","arrowsmithScore","jaccardScore","preferentialAttachmentScore")
otherNegData$class <- "Negative"
otherNegData <- otherNegData[,3:ncol(otherNegData)]
#otherNegData <- otherNegData[1:1000,]

meltedNegData <- melt(otherNegData,id="class")
colnames(meltedNegData) <- c("class","method","score")

# Combine everything

meltedData <- rbind(meltedNegData,meltedPosData,combinedSVDData)
meltedData$class <- as.factor(meltedData$class)


# And plot everything

names <- c("factaPlusScore","bitolaScore","anniScore","arrowsmithScore","jaccardScore","preferentialAttachmentScore","SVD")
titles <- c("FACTA","BITOLA","ANNI","Arrowsmith","Jaccard","Preferential Attachment","SVD")

#stopifnot(length(names)==length(titles))

png(outPlot, height = 750, width = 500, units = 'px')
cols <- 2
rows <- ceiling(length(names)/cols)
for (i in 1:length(names))
{
  name <- names[i]
  title <- titles[i]
  
  tmpPlot <- histogram(~score | class, meltedData[meltedData$method==name,], layout=c(1,2), main=title, col="white", par.settings = list(strip.background=list(col="lightgrey")))

  row <- floor((i+1)/cols)
  col <- ((i+1)%%cols)+1
  print(tmpPlot, split = c(col, row, cols, rows), more = !(i==length(names)))
  print(c(row,col))
}
dev.off()


