import argparse
import itertools
import numpy as np

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Calculate scores for candidate cooccurrences using the results of an SVD decomposition')
	parser.add_argument('--svdU',required=True,type=str,help='U component of SVD decomposition')
	parser.add_argument('--svdV',required=True,type=str,help='V component of SVD decomposition')
	parser.add_argument('--svdSV',required=True,type=str,help='SV component of SVD decomposition')
	parser.add_argument('--relationsToScore',type=str,help='Relations to calculate scores for')
	parser.add_argument('--idsFileA',type=str,help='File 1 containing IDs to check')
	parser.add_argument('--idsFileB',type=str,help='File 2 containing IDs to check')
	parser.add_argument('--sv',required=True,type=int,help='Number of singular values to use from SVD')
	parser.add_argument('--threshold',type=float,help='Optional argument to only output scores that are greater than a threshold')
	parser.add_argument('--outFile',required=True,type=str,help='Path to output file')
	args = parser.parse_args()

	threshold = None
	if args.threshold:
		threshold = args.threshold

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

	if args.relationsToScore:
		print "Loading relations to score..."
		relationsToScore = []
		with open(args.relationsToScore) as f:
			for line in f:
				x,y = line.strip().split()[0:2]
				x,y = int(x),int(y)
				relationsToScore.append((x,y))
		iterator = relationsToScore
	elif args.idsFileA and args.idsFileB:
		print "Loading IDs for scoring..."
		with open(args.idsFileA) as f:
			idsA = [ int(line.strip()) for line in f ]
		with open(args.idsFileB) as f:
			idsB = [ int(line.strip()) for line in f ]
		idsA = sorted(list(set(idsA)))
		idsB = sorted(list(set(idsB)))
		iterator = itertools.product(idsA,idsB)
	else:
		fullRange = svdU_lookup.keys()
		iterator = itertools.combinations(fullRange,2)
		#raise RuntimeError('Must either supply --relationsToScore or (--idsFileA and --idsFileA)')

	print "Calculating scores..."
	with open(args.outFile,'w') as outF:
		for x,y in iterator:
			# We only reconstruct one triangle of the matrix (where x<y)
			# Hence the min/max functions
			xIndex = svdU_lookup[min(x,y)]
			yIndex = svdV_lookup[max(x,y)]
			score = np.dot(svdU[xIndex,:],svdV[:,yIndex])
			if threshold is None or score > threshold:
				line = "%d\t%d\t%f\n" % (x,y,score)
				#print line
				outF.write(line)

	print "Scoring complete"
	print "Written to %s" % args.outFile

