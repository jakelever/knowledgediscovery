import argparse
import numpy as np

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Calculate scores for candidate cooccurrences using the results of an SVD decomposition')
	parser.add_argument('--svdU',required=True,type=str,help='U component of SVD decomposition')
	parser.add_argument('--svdV',required=True,type=str,help='V component of SVD decomposition')
	parser.add_argument('--svdSV',required=True,type=str,help='SV component of SVD decomposition')
	parser.add_argument('--relationsToScore',required=True,type=str,help='Relations to calculate scores for')
	parser.add_argument('--sv',required=True,type=int,help='Number of singular values to use from SVD')
	parser.add_argument('--outFile',required=True,type=str,help='Path to output file')
	args = parser.parse_args()

	print "Loading SVD U"
	svdU = np.loadtxt(args.svdU)
	svdU_index = map(int,svdU[:,0].tolist())
	svdU_lookup = { x:i for i,x in enumerate(svdU_index) }
	svdU = svdU[:,1:]
	print "len(svdU_index) = ", len(svdU_index)
	print "svdU.shape = ", svdU.shape

	print "Loading SVD V"
	svdV = np.loadtxt(args.svdV)
	svdV_index = map(int,svdV[:,0].tolist())
	svdV_lookup = { x:i for i,x in enumerate(svdV_index) }
	svdV = svdV[:,1:]
	print "len(svdV_index) = ", len(svdV_index)
	print "svdV.shape = ", svdV.shape

	print "Loading SVD SV"
	svdSV = np.loadtxt(args.svdSV, comments="%")
	print "svdSV.shape = ", svdSV.shape

	print "Truncating data..."
	svdU = svdU[:,:args.sv]
	svdV = svdV[:,:args.sv]
	svdSV = svdSV[:args.sv]
	print "svdU.shape = ", svdU.shape
	print "svdV.shape = ", svdV.shape
	print "svdSV.shape = ", svdSV.shape

	print "Pre-multiplying svdV by svdSV"
	svdV = np.dot(np.diag(svdSV),svdV.T)
	print "svdV.shape = ", svdV.shape

	print "Loading relations to score..."
	relationsToScore = set()
	with open(args.relationsToScore) as f:
		for line in f:
			x,y = line.strip().split()[0:2]
			x,y = int(x),int(y)
			if x > y:
				x,y = y,x
			relationsToScore.add((x,y))
	relationsToScore = sorted(list(relationsToScore))

	print "Calculating scores..."
	with open(args.outFile,'w') as outF:
		for x,y in relationsToScore:
			xIndex = svdU_lookup[x]
			yIndex = svdV_lookup[y]
			score = np.dot(svdU[xIndex,:],svdV[:,yIndex])
			line = "%d\t%d\t%f\n" % (x,y,score)
			#print line
			outF.write(line)

	print "Scoring complete"
	print "Written to %s" % args.outFile

