import sys
import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Sanity check to make sure that a cooccurrence file has been filtered correctly')
	parser.add_argument('--cooccurrenceFile',required=True,type=str,help='Cooccurrence file to check')
	parser.add_argument('--acceptedIDs',required=True,type=str,help='IDs that can be accepted')
	parser.add_argument('--previousCooccurrences',required=True,type=str,help='Cooccurrences that should have been filtered out')
	args = parser.parse_args()

	with open(args.acceptedIDs) as f:
		acceptedIDs = [ int(line.strip()) for line in f ]
		acceptedIDs = set(acceptedIDs)

	with open(args.previousCooccurrences) as f:
		previousCooccurrences = set()
		for line in f:
			x,y = line.strip().split()[:2]
			x,y = int(x),int(y)
			previousCooccurrences.add((x,y))

	with open(args.cooccurrenceFile) as f:
		for line in f:
			x,y,_ = line.strip().split('\t')
			x,y = int(x),int(y)
			if not x in acceptedIDs:
				print "Found ID %d in cooccurrence file %s" % (x,args.cooccurrenceFile)
				sys.exit(255)
			if not y in acceptedIDs:
				print "Found ID %d in cooccurrence file %s" % (y,args.cooccurrenceFile)
				sys.exit(255)
			if (x,y) in previousCooccurrences:
				print "Found previous cooccurrence (%d,%d) in cooccurrence file %s" % (x,y,args.cooccurrenceFile)
				sys.exit(255)


	print "File %s has been filtered correctly" % args.cooccurrenceFile

