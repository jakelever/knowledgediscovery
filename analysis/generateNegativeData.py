import argparse
import random

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Generate cooccurrence data for use in testing as negative data points')
	parser.add_argument('--trueData',type=str,required=True,help='Path to cooccurrences that are true')
	parser.add_argument('--knownConceptIDs',type=str,required=True,help='Path to file containing known IDs (occurrences in training data)')
	parser.add_argument('--num',type=int,required=True,help='Number of negative cooccurrences to generate')
	parser.add_argument('--outFile',type=str,required=True,help='Path to output file')

	args = parser.parse_args()

	print "Loading trueData..."
	trueData = set()
	with open(args.trueData) as f:
		for line in f:
			x,y,_ = line.strip().split()
			x,y = int(x),int(y)
			if x>y:
				x,y = y,x

			trueData.add((x,y))
	print "Loaded trueData"

	print "Loading knownConceptIDs..."
	knownConceptIDs = set()
	with open(args.knownConceptIDs) as f:
		for line in f:
			x = line.strip().split()[0]
			x = int(x)

			knownConceptIDs.add(x)
	print "Loaded knownConceptIDs"

	print "Starting negative data generation..."
	with open(args.outFile,'w') as outF:
		used = set()
		nextPerc = 0.0
		while len(used) < args.num:
			x,y = random.sample(knownConceptIDs,2)
			if x>y:
				x,y = y,x

			if (x,y) in used:
				continue

			if (x,y) in trueData:
				continue

			used.add((x,y))
			outF.write("%d\t%d\t%d\n" % (x,y,0))

			perc = 100.0 * float(len(used)) / float(args.num)
			if perc > nextPerc:
				print "%.1f%% complete" % perc
				nextPerc += 1.0

	print "False data generation complete."
	print "Written to %s" % args.outFile
			

