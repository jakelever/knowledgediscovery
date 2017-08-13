import argparse
import numpy as np
				
def calculateANNIScore(x,z,conceptVectorsIndex,conceptVectors):
	indexX = conceptVectorsIndex[x]
	indexZ = conceptVectorsIndex[z]
	
	vectorX = conceptVectors[indexX,:]
	vectorZ = conceptVectors[indexZ,:]
	dotprod = np.dot(vectorX,vectorZ)
	return dotprod

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Calculate scores for a set of scores')
	parser.add_argument('--cooccurrenceFile',type=str,required=True,help='File containing cooccurrences')
	parser.add_argument('--occurrenceFile',type=str,required=True,help='File containing occurrences')
	parser.add_argument('--sentenceCount',type=str,required=True,help='File containing sentence count')
	parser.add_argument('--relationsToScore',type=str,required=True,help='File containing relations to score')
	parser.add_argument('--anniVectors',type=str,help='File containing the raw ANNI vector data')
	parser.add_argument('--anniVectorsIndex',type=str,help='File containing the index for the ANNI vector data')
	parser.add_argument('--outFile',type=str,required=True,help='File to output scores to')

	args = parser.parse_args()

	print "Loading relationsToScore"
	relationsToScore = []
	entitiesToScore = set()
	with open(args.relationsToScore) as f:
		for line in f:
			split = map(int,line.strip().split())
			x,y = split[:2]
			relationsToScore.append((x,y))
			entitiesToScore.add(x)
			entitiesToScore.add(y)
	entitiesToScore = sorted(list(entitiesToScore))
	print "Loaded relationsToScore"

	doANNI = args.anniVectorsIndex and args.anniVectors
	if doANNI:
		print "Loading ANNI concept vectors..."
		#anniConceptVectors = prepareANNIConceptVectors(entitiesToScore,neighbours,cooccurrences,occurrences,sentenceCount)
		with open(args.anniVectorsIndex) as f:
			anniVectorsIndex = { int(line.strip()):i for i,line in enumerate(f) }
		
		with open(args.anniVectors,'rb') as f:
			anniConceptVectors = np.fromfile(f,np.float32)
			vectorSize = int(anniConceptVectors.shape[0] / len(anniVectorsIndex))
			anniConceptVectors = anniConceptVectors.reshape((len(anniVectorsIndex),vectorSize))

			#print "Normalising ANNI concept vectors"
			#l2norm = np.sqrt((anniConceptVectors * anniConceptVectors).sum(axis=1))
			#anniConceptVectors = anniConceptVectors / l2norm.reshape(anniConceptVectors.shape[0],1)

		print "Loaded ANNI concept vectors"

	print "Scoring..."
	with open(args.outFile,'w') as outF:
		for i,(x,z) in enumerate(relationsToScore):
			if (i%10000) == 0:
				print i
		
			anniScore = calculateANNIScore(x,z,anniVectorsIndex,anniConceptVectors)
			outData = [x,z,anniScore]
	
			outLine = "\t".join(map(str,outData))
			outF.write(outLine+"\n")

	print "Completed scoring"
	print "Output to %s" % args.outFile

