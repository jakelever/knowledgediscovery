
library(lattice)

args <- commandArgs(TRUE)

inData <- args[1]
outPlot <- args[2]

data <- read.table(inData)

colnames(data) <- c('analysisName', 'true_positive_rate', 'false_positive_rate', 'adjusted_precision', 'adjusted_f1Score', 'tp', 'fp', 'tn', 'fn', 'threshold')

data <- data[order(data$true_positive_rate,data$adjusted_precision),]

tiff(outPlot)
xyplot(adjusted_precision~true_positive_rate,data,groups=analysisName,type="l",xlim=c(0,1),ylim=c(0,1),auto.key=T)
dev.off()

