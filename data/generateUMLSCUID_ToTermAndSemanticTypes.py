import sys
import argparse
from collections import defaultdict
import string

if __name__ == "__main__":

	# Set up the command line arguments
	parser = argparse.ArgumentParser(description='Generates a mapping from CUID to main term and semantic types based on UMLS files')
	
	parser.add_argument('--umlsConceptFile', required=True, type=argparse.FileType('r'), help='The concept file from the UMLS dataset')
	parser.add_argument('--umlsSemanticTypesFile', required=True, type=argparse.FileType('r'), help='The semantic types file from the UMLS dataset')
	
	parser.add_argument('--outFile', required=True, type=argparse.FileType('w'), help='Path to mapping')
	args = parser.parse_args()
	
	# We're only extracting terms in English
	defaultLanguage = 'ENG'
	
	semanticTypes = defaultdict(set)	
	# Get a list of Concept IDs (CUIDs) that are of a semantic type that we want
	print "Associating CUIDs with semantic type..."
	for line in args.umlsSemanticTypesFile:
		split = line.strip().split('|')
		cuid = split[0]
		semanticTypeID = split[1]
		semanticTypes[cuid].add(semanticTypeID)
			
	# Get the actual terms used for each of the CUIDs that we're interesting in
	print "Extracting term for CUIDs..."
	conceptTerms = {}
	for line in args.umlsConceptFile:
		split = line.strip().split('|')
		cuid = split[0]
		language = split[1]
		term = split[14]
		
		# Filter for the concept IDs already discovered
		if language == defaultLanguage and not cuid in conceptTerms:
			conceptTerms[cuid] = term
	
	cuids = sorted(list(conceptTerms.keys()))

	# And now we can simply output the CUIDs, semantic types and terms
	print "Saving mapping..."
	for cuid in cuids:
		assert cuid in semanticTypes
		assert cuid in conceptTerms

		# Get all the semantic type IDs associated with this CUID
		theseSemanticTypes = sorted(list(semanticTypes[cuid]))
		
		# Get all main term associated with this CUID
		thisTerm = conceptTerms[cuid]
		
		# Output them to the wordlist as a 3 column file (where each column is pipe-delimited)
		line = "%s\t%s\t%s" % (cuid,"|".join(theseSemanticTypes),thisTerm)
		args.outFile.write(line + "\n")
		
