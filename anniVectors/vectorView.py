import argparse
import numpy as np

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='View the ANNI vector file (for debug purposes)')
	parser.add_argument('--anniVectors',type=str,required=True,help='File containing the raw ANNI vector data')
	parser.add_argument('--anniVectorsIndex',type=str,required=True,help='File containing the index for the ANNI vector data')
	parser.add_argument('--outFile',type=str,required=True,help='File to output scores to')
	args = parser.parse_args()

	print "Loading ANNI concept vectors..."
	with open(args.anniVectorsIndex) as f:
		anniVectorsIndex = { int(line.strip()):i for i,line in enumerate(f) }

	with open(args.anniVectors,'rb') as f:
		anniConceptVectors = np.fromfile(f,np.float32)
		vectorSize = int(anniConceptVectors.shape[0] / len(anniVectorsIndex))
		anniConceptVectors = anniConceptVectors.reshape((len(anniVectorsIndex),vectorSize))

	print "Saving ANNI vectors..."
	with open(args.outFile,'w') as outF:
		for conceptID,row in anniVectorsIndex.iteritems():
			outData = [conceptID] + anniConceptVectors[row,:].tolist()
			outLine = "\t".join(map(str,outData))
			outF.write(outLine+"\n")
	print "Saved ANNI vectors"

