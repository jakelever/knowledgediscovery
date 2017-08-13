import argparse
from collections import defaultdict

def calculateAverageMinimumWeight(x,z,neighbours,cooccurrences):
	shared = neighbours[x].intersection(neighbours[z])
	if len(shared) == 0:
		return 0

	total = 0.0
	for y in shared:
		total += min(cooccurrences[(x,y)],cooccurrences[(y,z)])
	return total / float(len(shared))
	
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

	print "Loading cooccurrences..."
	cooccurrences = {}
	neighbours = defaultdict(set)
	with open(args.cooccurrenceFile) as f:
		for line in f:
			x,y,count = map(int,line.strip().split())
			cooccurrences[(x,y)] = count
			cooccurrences[(y,x)] = count
			neighbours[x].add(y)
			neighbours[y].add(x)
	print "Loaded cooccurrences"

	print "Scoring..."
	with open(args.outFile,'w') as outF:
		for i,(x,z) in enumerate(relationsToScore):
			if (i%10000) == 0:
				print i
	
			amwScore = calculateAverageMinimumWeight(x,z,neighbours,cooccurrences)

			outData = [x,z,amwScore]
			outLine = "\t".join(map(str,outData))
			outF.write(outLine+"\n")

	print "Completed scoring"
	print "Output to %s" % args.outFile

