import argparse
import codecs
import numpy as np

def calculateANNIScore(x,z,conceptVectorsIndex,conceptVectors):
	indexX = conceptVectorsIndex[x]
	indexZ = conceptVectorsIndex[z]

	vectorX = conceptVectors[indexX,:]
	vectorZ = conceptVectors[indexZ,:]
	dotprod = np.dot(vectorX,vectorZ)

	return dotprod

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Calculate the nearest terms to a given term')
	parser.add_argument('--wordlistWithCUIDs',type=str,required=True,help='UMLS wordlist with CUID and style IDs (three column file)')
	parser.add_argument('--anniVectors',type=str,required=True,help='File containing the raw ANNI vector data')
	parser.add_argument('--anniVectorsIndex',type=str,required=True,help='File containing the index for the ANNI vector data')
	parser.add_argument('--cuid',type=str,required=True,help='CUID of target term')
	parser.add_argument('--outFile',type=str,required=True,help='Output file to dump term comparisons')

	args = parser.parse_args()

	print "Loading ANNI concept vectors..."
	with open(args.anniVectorsIndex) as f:
		anniVectorsIndex = { int(line.strip()):i for i,line in enumerate(f) }

	with open(args.anniVectors,'rb') as f:
		anniConceptVectors = np.fromfile(f,np.float32)
		vectorSize = int(anniConceptVectors.shape[0] / len(anniVectorsIndex))
		anniConceptVectors = anniConceptVectors.reshape((len(anniVectorsIndex),vectorSize))

	allEntities = sorted(list(anniVectorsIndex.keys()))
	targetEntity = None

	print "Loading wordlist"
	with codecs.open(args.wordlistWithCUIDs,'r','utf8') as f:
		wordlist = {}
		for i,line in enumerate(f):
			split = line.strip().split('\t')
			cuid = split[0]
			terms = split[2].split('|')
			firstterm = terms[0]

			wordlist[i] = (cuid,firstterm)

			if cuid == args.cuid:
				targetEntity = i

	assert not targetEntity is None
	assert targetEntitiy in allEntities

	print "Starting scoring"
	scores = []
	for e in allEntities:
		score = calculateANNIScore(e,targetEntity,anniVectorsIndex,anniConceptVectors)
		scores.append((score,e))

	print "Sorting scores"
	scores = sorted(scores,reverse=True)

	print "Saving to file"
	with codecs.open(args.outFile,'w','utf8') as outF:
		for (score,e) in scores:
			cuid,term = wordlist[e]
			outData = [str(score),cuid,term]
			outLine = u"\t".join(outData)
			outF.write(outLine + u"\n")

	print "Complete"

