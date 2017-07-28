
library(lattice)
library(RColorBrewer)

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
data$analysisName[data$analysisName=='amw'] <- 'AMW'
data$analysisName[data$analysisName=='ltc-amw'] <- 'LTC-AMW'
data$analysisName[grep('SVD',data$analysisName)] <- 'SVD'


myColours <- c(brewer.pal(8,"Dark2"),"#000000")
my.settings <- list(
  superpose.polygon=list(col=myColours),
  strip.background=list(col=myColours),
  superpose.line=list(col=myColours),
  strip.border=list(col="black")
)

png(outPlot)
#setEPS()
#postscript(outPlot)
xyplot(adjusted_precision~true_positive_rate,
       data,groups=analysisName,
       type="l",
       xlim=c(0,1),
       ylim=c(0,1),
       auto.key=list(space="top", columns=3, 
                     points=FALSE, rectangles=TRUE),
       par.settings = my.settings,
       xlab="Recall",
       ylab="Precision",
       lwd=2)
dev.off()

