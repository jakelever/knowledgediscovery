
library(lattice)
library(reshape)

inSVDData <- 'H:/Downloads/scores.testing.svd'
inOtherData <- 'H:/Downloads/scores.testing.other'
inClasses <- 'H:/Downloads/combinedData.testing.classes'

# Load the class data (binary)
classData <- read.table(inClasses)
colnames(classData) <- c('class')

# First load the SVD specific data
svdData <- read.table(inSVDData)
colnames(svdData) <- c('idX','idY','score')

# Then load the other methods data
otherData <- read.table(inOtherData)
colnames(otherData) <- c("idX","idY","factaPlusScore","bitolaScore","anniScore","arrowsmithScore","jaccardScore","preferentialAttachmentScore","amwScore","ltcamwScore")

# Merge in the SVD scores and class data
otherData$svdScore <- svdData$score
otherData$class <- classData$class

# Remove the coordinates (don't need them)
otherData <- otherData[,3:ncol(otherData)]

# Melt the data so that method becomes a column (and rename the columns appropriately)
meltedData <- melt(otherData,id="class")
colnames(meltedData) <- c("class","method","score")

# Rename the classes to Positive/Negative
meltedData$class[meltedData$class==0] <- 'Negative'
meltedData$class[meltedData$class==1] <- 'Positive'

meltedData$class <- as.factor(meltedData$class)

# Organise how the columns should be mapped to titles for each subfigure
names <- c("amwScore","anniScore","arrowsmithScore","bitolaScore","factaPlusScore","jaccardScore","ltcamwScore","preferentialAttachmentScore","svdScore")
titles <- c("AMW","ANNI","Arrowsmith","BITOLA","FACTA+","Jaccard","LTC-AMW","Preferential Attachment","SVD")


calcPRAUC <- function(method,classBalance) {
  method <- as.character(method)
  data <- meltedData[meltedData$method == method,]
  data$class <- (data$class == 'Positive')
  
  invClassBalance <- 1-classBalance
  
  data <- data[order(data$score,decreasing=T),]
  data$posCount <- 0
  data$negCount <- 0
  data$posCount[data$class==T] <- 1 #classBalance
  data$negCount[data$class==F] <- 1 #1-classBalance
  
  data$TP <- cumsum(data$posCount)
  data$FP <- cumsum(data$negCount)
  
  allPosCount <- sum(data$class)
  allNegCount <- nrow(data) - allPosCount
  data$TN <- allNegCount - data$FP
  data$FN <- allPosCount - data$TP
  
  data$adjPrecision <- classBalance*data$TP / (classBalance*data$TP + invClassBalance*data$FP)
  data$recall <- data$TP / (data$TP + data$FN)
  
  #xyplot(adjPrecision ~ recall, data, type="l")
  
  auc <- AUC(c(data$recall,1), c(data$adjPrecision,0))
  
  return(auc)
}


classBalance <- .00141446976033217173

grid <- expand.grid(method=c('arrowsmithScore','amwScore','svdScore'),classBalance=c(classBalance,.05,.1,.15,.2,.25,.3,.35,.4,.45,.5))
#grid <- data.frame(method='svdScore',classBalance=classBalance)

grid$prauc <- mapply(calcPRAUC, grid$method, grid$classBalance)

myColours <- c(brewer.pal(8,"Dark2"),"#000000")
my.settings <- list(
  superpose.polygon=list(col=myColours),
  strip.background=list(col=myColours),
  superpose.line=list(col=myColours),
  strip.border=list(col="black")
)

grid$method <- as.character(grid$method)
grid$method[grid$method=='svdScore'] <- 'SVD'
grid$method[grid$method=='arrowsmithScore'] <- 'Arrowsmith'
grid$method[grid$method=='amwScore'] <- 'AMW'

xyplot( prauc ~ classBalance, 
        grid, 
        groups=method, 
        auto.key=list(space="top", columns=3, 
                      points=FALSE, rectangles=TRUE),
        par.settings = my.settings,
        type="l",
        xlab="Class balance",
        ylab="Area under the Precision-Recall Curve",
        lwd=2,
        xlim=c(0,0.5))

