
library(lattice)

args <- commandArgs(TRUE)

inData <- args[1]
outPlot <- args[2]

data <- read.table(inData)
colnames(data) <- c("year","total","predicted")
data$year <- as.factor(as.character(data$year))
data$recall <- data$predicted/data$total


tiff(outPlot)
barchart( recall ~ year, data, horizontal=F, ylim=c(0,1.1*max(data$recall)), col="black")
dev.off()

