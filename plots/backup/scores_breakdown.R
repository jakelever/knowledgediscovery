
library(lattice)
library(reshape)

args <- commandArgs(TRUE)

inSVDData <- args[1]
inOtherData <- args[2]
inClasses <- args[3]
outPlot <- args[4]

classData <- read.table(inClasses)
colnames(classData) <- c('class')

# First load the SVD specific data
svdData <- read.table(inSVDData)
colnames(svdData) <- c('idX','idY','score')

# Then load the other methods data

otherData <- read.table(inOtherData)
colnames(otherData) <- c("idX","idY","factaPlusScore","bitolaScore","anniScore","arrowsmithScore","jaccardScore","preferentialAttachmentScore")
otherData$svdScore <- svdData$score
otherData$class <- classData$class
otherData <- otherData[,3:ncol(otherData)]

meltedData <- melt(otherData,id="class")
colnames(meltedData) <- c("class","method","score")

meltedData$class[meltedData$class==0] <- 'Negative'
meltedData$class[meltedData$class==1] <- 'Positive'

meltedData$class <- as.factor(meltedData$class)


# And plot everything

#names <- c("factaPlusScore","bitolaScore","anniScore","arrowsmithScore","jaccardScore","preferentialAttachmentScore","svdScore")
#titles <- c("FACTA","BITOLA","ANNI","Arrowsmith","Jaccard","Preferential Attachment","SVD")
names <- c("anniScore","arrowsmithScore","bitolaScore","factaPlusScore","jaccardScore","preferentialAttachmentScore","svdScore")
titles <- c("ANNI","Arrowsmith","BITOLA","FACTA+","Jaccard","Preferential Attachment","SVD")
#stopifnot(length(names)==length(titles))

png(outPlot, height = 750, width = 500, units = 'px')
#setEPS()
#postscript(outPlot, height = 750, width = 500, units = 'px')
#postscript(outPlot)
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


