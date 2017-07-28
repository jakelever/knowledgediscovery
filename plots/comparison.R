
library(lattice)

args <- commandArgs(TRUE)

inData <- args[1]
outPlot <- args[2]

data <- read.table(inData)
data <- data[,c(1,3)]
colnames(data) <- c("method","areaUnderPRCurve")

data$method <- as.character(data$method)
data$method[data$method=='anni'] <- 'ANNI'
data$method[data$method=='preferentialAttachment'] <- 'Preferential Attachment'
data$method[data$method=='factaPlus'] <- 'FACTA+'
data$method[data$method=='jaccard'] <- 'Jaccard'
data$method[data$method=='arrowsmith'] <- 'Arrowsmith'
data$method[data$method=='bitola'] <- 'BITOLA'
data$method[data$method=='amw'] <- 'AMW'
data$method[data$method=='ltc-amw'] <- 'LTC-AMW'
data$method[grep('SVD',data$method)] <- 'SVD'

png(outPlot)
#setEPS()
#postscript(outPlot)
barchart( areaUnderPRCurve ~ method, data, col="black",scales=list(x=list(rot=45)), xlab="Method", ylab="Area Under the Precision Recall curve")
dev.off()

