
library(lattice)

args <- commandArgs(TRUE)

inData <- args[1]
outPlot <- args[2]

data <- read.table(inData)

data <- data[,c(1,3)]
colnames(data) <- c("Method","AreaUnderPRCurve")

png(outPlot)
barchart( AreaUnderPRCurve ~ Method, data, col="black")
dev.off()

