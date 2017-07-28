
library(lattice)

args <- commandArgs(TRUE)

inData <- args[1]
outPlot <- args[2]

data <- read.table(inData)

colnames(data) <- c('analysisName', 'true_positive_rate', 'false_positive_rate', 'adjusted_precision', 'adjusted_f1Score', 'tp', 'fp', 'tn', 'fn', 'threshold')

data <- data[order(data$true_positive_rate,data$adjusted_precision),]

data$analysisName <- as.character(data$analysisName)
data$analysisName[data$analysisName=='anni'] <- 'ANNI'
data$analysisName[data$analysisName=='preferentialAttachment'] <- 'Preferential Attachment'
data$analysisName[data$analysisName=='factaPlus'] <- 'FACTA+'
data$analysisName[data$analysisName=='jaccard'] <- 'Jaccard'
data$analysisName[data$analysisName=='arrowsmith'] <- 'Arrowsmith'
data$analysisName[data$analysisName=='bitola'] <- 'BITOLA'
data$analysisName[grep('SVD',data$analysisName)] <- 'SVD'

setEPS()
postscript(outPlot)
xyplot(adjusted_precision~true_positive_rate,data,groups=analysisName,type="l",xlim=c(0,1),ylim=c(0,1),auto.key=T,xlab="Recall",ylab="Precision")
dev.off()

