import argparse
import itertools

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Generate the cartesian product of two ID files')
	parser.add_argument('--idFileA',required=True,type=str,help='First file of IDs')
	parser.add_argument('--idFileB',required=True,type=str,help='Second file of IDS')
	parser.add_argument('--outFile',required=True,type=str,help='Output file')
	args = parser.parse_args()

	with open(args.idFileA) as f:
		idsA = [ int(line.strip()) for line in f ]
	with open(args.idFileB) as f:
		idsB = [ int(line.strip()) for line in f ]

	idsA = sorted(list(set(idsA)))
	idsB = sorted(list(set(idsB)))

	with open(args.outFile,'w') as outF:
		for a,b in itertools.product(idsA,idsB):
			outF.write("%d\t%d\n" % (min(a,b),max(a,b)))
	
	print "Processing complete."
