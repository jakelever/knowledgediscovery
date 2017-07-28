
library(lattice)

args <- commandArgs(TRUE)

inData <- args[1]
outPlot <- args[2]

data <- read.table(inData)
colnames(data) <- c("year","total","predicted")
data$year <- as.factor(as.character(data$year))
data$recall <- data$predicted/data$total

# Trim out the 2017 data because it has a very small number of points and is an unfair comparison
data <- data[data$year!=2017,]

png(outPlot)
#setEPS()
#postscript(outPlot)
barchart( recall ~ year, data, horizontal=F, ylim=c(0,1.1*max(data$recall)), col="black",xlab="Year for Test Data",ylab="Recall")
dev.off()

