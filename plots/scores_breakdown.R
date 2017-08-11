
library(lattice)
library(reshape)

args <- commandArgs(TRUE)

inSVDData <- args[1]
inOtherData <- args[2]
inClasses <- args[3]
outPlot <- args[4]

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

# Then we do lots of sub-plots and merge them together
#png(outPlot, height = 1000, width = 500, units = 'px')
setEPS()
postscript(outPlot, height=16, width=6)
cols <- 2
rows <- ceiling(length(names)/cols)
for (i in 1:length(names))
{
  name <- names[i]
  title <- titles[i]
  
  #tmpPlot <- histogram(~score | class, meltedData[meltedData$method==name,], layout=c(1,2), main=title, col="white", par.settings = list(strip.background=list(col="lightgrey")))
  #tmpPlot <- densityplot(~score | class, meltedData[meltedData$method==name,], plot.points = FALSE, layout=c(1,2), main=title, col="black", par.settings = list(strip.background=list(col="lightgrey")))
    tmpPlot <- bwplot(~score|class,
	data=meltedData[meltedData$method==name,], 
	horizontal=TRUE,
	layout=c(1,2),
	panel = function(..., box.ratio) {
	panel.violin(..., col = "gray",
	varwidth = FALSE, box.ratio = box.ratio)
	#panel.bwplot(..., col='black',
	#             cex=0.8, pch='|', fill='white', box.ratio = .1)
	},
	par.settings = list(box.rectangle=list(col='black'),
	plot.symbol = list(pch='.', cex = 0.1),
	strip.background=list(col="lightgrey")),
	main=title
	)

  row <- floor((i+1)/cols)
  col <- ((i+1)%%cols)+1
  print(tmpPlot, split = c(col, row, cols, rows), more = !(i==length(names)))
  print(c(row,col))
}
dev.off()


