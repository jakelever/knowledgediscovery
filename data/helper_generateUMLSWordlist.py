import sys
import argparse
from collections import defaultdict
import string

if __name__ == "__main__":

	# Set up the command line arguments
	parser = argparse.ArgumentParser(description='Generates a wordlist based on UMLS files and required semantic types and relationship types')
	parser.add_argument('--selectedTypeIDs', required=True, type=str, help='Comma-delimited list of type IDs that should be included in the word-list')
	parser.add_argument('--selectedRelTypes', type=str, help='Comma-delimited list of relationship types that should be included in the word-list (e.g. has_tradename)')
	
	parser.add_argument('--umlsConceptFile', required=True, type=argparse.FileType('r'), help='The concept file from the UMLS dataset')
	parser.add_argument('--umlsSemanticTypesFile', required=True, type=argparse.FileType('r'), help='The semantic types file from the UMLS dataset')
	
	parser.add_argument('--outWordlistFile', required=True, type=argparse.FileType('w'), help='Path to output word-list to')
	args = parser.parse_args()
	
	# We're only extracting terms in English
	defaultLanguage = 'ENG'
	
	# Get the SemanticTypeIDs and Relationship types that will be filtered for
	selectedTypeIDs = set(args.selectedTypeIDs.split(','))
	
	filteredConceptIDs = set()
	filteredConceptSemanticTypeIDs = defaultdict(list)
	
	# Get a list of Concept IDs (CUIDs) that are of a semantic type that we want
	print "Filtering CUIDs by semantic type..."
	for line in args.umlsSemanticTypesFile:
		split = line.strip().split('|')
		cuid = split[0]
		semanticTypeID = split[1]
		
		# Filter for the semantic types of interest
		if semanticTypeID in selectedTypeIDs:
			filteredConceptIDs.add(cuid)
			filteredConceptSemanticTypeIDs[cuid].append(semanticTypeID)
			
	# Get the actual terms used for each of the CUIDs that we're interesting in
	print "Extracting terms for filtered CUIDs..."
	filteredConceptsTerms = defaultdict(list)
	for line in args.umlsConceptFile:
		split = line.strip().split('|')
		cuid = split[0]
		language = split[1]
		term = split[14]
		
		# Filter for the concept IDs already discovered
		if language == defaultLanguage and cuid in filteredConceptIDs:
			filteredConceptsTerms[cuid].append(term.lower())
	
	
	# And now we can simply output the filtered CUIDs, semantic types and terms
	print "Saving word-list..."
	for cuid in filteredConceptsTerms:
		
		# Get all the semantic type IDs associated with the list of CUIDs
		semanticTypeIDs = [ semanticTypeID for semanticTypeID in filteredConceptSemanticTypeIDs[cuid] ]
		
		# Get all the terms associated with the list of CUIDs
		terms = [ term for term in filteredConceptsTerms[cuid] ]
			
		# Sort and unique each of the lists (just in case)
		semanticTypeIDs = sorted(list(set(semanticTypeIDs)))
		terms = sorted(list(set(terms)))
		
		# Output them to the wordlist as a 3 column file (where each column is pipe-delimited)
		line = "%s\t%s\t%s" % (cuid,"|".join(semanticTypeIDs),"|".join(terms))
		args.outWordlistFile.write(line + "\n")
		
