import sys
import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Sanity check to make sure that a occurrence file has been filtered correctly')
	parser.add_argument('--occurrenceFile',required=True,type=str,help='Occurrence file to check')
	parser.add_argument('--acceptedIDs',required=True,type=str,help='IDs that can be accepted')
	args = parser.parse_args()

	with open(args.acceptedIDs) as f:
		acceptedIDs = [ int(line.strip()) for line in f ]
		acceptedIDs = set(acceptedIDs)

	with open(args.occurrenceFile) as f:
		for line in f:
			x,_ = line.strip().split('\t')
			x = int(x)
			if not x in acceptedIDs:
				print "Found ID %d in occurrence file %s" % (x,args.occurrenceFile)
				sys.exit(255)

	print "File %s has been filtered correctly" % args.occurrenceFile
