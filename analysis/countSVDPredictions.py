import argparse
import itertools
import numpy as np
from collections import defaultdict

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Calculate scores for candidate cooccurrences using the results of an SVD decomposition')
	parser.add_argument('--svdU',required=True,type=str,help='U component of SVD decomposition')
	parser.add_argument('--svdV',required=True,type=str,help='V component of SVD decomposition')
	parser.add_argument('--svdSV',required=True,type=str,help='SV component of SVD decomposition')
	parser.add_argument('--relationsToIgnore',type=str,help='Relations to ignore in count')
	parser.add_argument('--sv',required=True,type=int,help='Number of singular values to use from SVD')
	parser.add_argument('--idsFile',required=True,type=str,help='File containing IDs to iterate over')
	parser.add_argument('--threshold',required=True,type=float,help='Optional argument to only output scores that are greater than a threshold')
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

	relationsToIgnore = defaultdict(set)
	if args.relationsToIgnore:
		print "Loading relations to score..."
		with open(args.relationsToIgnore) as f:
			for line in f:
				x,y = line.strip().split()[0:2]
				x,y = int(x),int(y)
				#relationsToScore.append((x,y))
				relationsToIgnore[x].add(y)
				relationsToIgnore[y].add(x)
		
		translatedRelationsToIgnore_U = {}
		translatedRelationsToIgnore_V = {}
		for k in relationsToIgnore.keys():
			relationsToIgnore[k] = sorted(list(relationsToIgnore[k]))
			translatedRelationsToIgnore_U[k] = [ svdU_lookup[x] for x in relationsToIgnore[k] ]
			translatedRelationsToIgnore_V[k] = [ svdV_lookup[x] for x in relationsToIgnore[k] ]

	with open(args.idsFile) as f:
		ids = [ int(line.strip()) for line in f ]

	print "Calculating scores..."
	predCount = 0
	for row in ids:
		# We only reconstruct one triangle of the matrix (where x<y)
		# Hence the min/max functions
		#xIndex = svdU_lookup[min(x,y)]
		#xIndex = svdU_lookup[row]
		yIndex = svdV_lookup[row]
		#scores = np.dot(svdU[xIndex,:],svdV)
		scores = np.dot(svdU,svdV[:,yIndex])
		
		mask = np.zeros((len(ids)))
		mask[range(svdU_lookup[row])] = 1
		mask[translatedRelationsToIgnore_U[row]] = 0
		
		maskedScores = scores * mask
		tmpCount = (maskedScores > threshold).sum()

		#if tmpCount > 0:
		#	where = np.where(maskedScores > threshold)
		#	print scores[where]
		#	print row,where

		predCount += tmpCount

	print "Scoring complete"


	with open(args.outFile,'w') as outF:
		outF.write("%d\n" % predCount)
	print "Written to %s" % args.outFile

