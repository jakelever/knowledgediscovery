import sys
import xml.etree.ElementTree as etree
import argparse
import os.path

# It's the main bit. Yay!
if __name__ == "__main__":

	# From StackOverflow: http://stackoverflow.com/questions/11415570/directory-path-types-with-argparse
	def readable_dir(prospective_dir):
		if not os.path.isdir(prospective_dir):
			raise Exception("readable_dir:{0} is not a valid path".format(prospective_dir))
		if os.access(prospective_dir, os.R_OK):
			return prospective_dir
		else:
			raise Exception("readable_dir:{0} is not a readable dir".format(prospective_dir))
			
	def existing_filepath(prospective_filepath):
		if os.path.exists(prospective_filepath):
			return prospective_filepath
		else:
			raise Exception("existing_filepath:{0} does not exist".format(prospective_filepath))

	# Arguments for the command line
	parser = argparse.ArgumentParser(description='Extracts MEDLINE XML files and splits them into files based on publication years')
	parser.add_argument('--medlineXML', type=existing_filepath, help='Path to a single MedlineXML file')
	parser.add_argument('--outDir', type=readable_dir, help='The output directory to store the split Medline files')
	parser.add_argument('--pmidExclusionFile', type=existing_filepath, help='A file of PMIDs to exclude')

	args = parser.parse_args()
	
	header = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE MedlineCitationSet PUBLIC "-//NLM//DTD Medline Citation, 1st January, 2015//EN"\n                                    "http://www.nlm.nih.gov/databases/dtd/nlmmedlinecitationset_150101.dtd">\n<MedlineCitationSet>\n'
	footer = '</MedlineCitationSet>\n'
	
	pmidExclusions = {}
	with open(args.pmidExclusionFile) as f:
		for line in f:
			pmid = int(line.strip())
			pmidExclusions[pmid] = True
	
	handles = {}
	
	basenameWithoutExt = os.path.splitext(os.path.basename(args.medlineXML))[0]
	outDir = args.outDir
	if outDir[-1] != '/':
		outDir = outDir + '/'

	print "Starting processing:", args.medlineXML

	count = 0
	for event, elem in etree.iterparse(args.medlineXML, events=('start', 'end', 'start-ns', 'end-ns')):
		if (event=='end' and elem.tag=='MedlineCitation'):
			count = count + 1
			if (count % 1000 == 0):
				print args.medlineXML + "\t" + str(count)
			
			try:
				pmid = int(elem.findall('./PMID')[0].text)
				
				if pmid in pmidExclusions:
					print >> sys.stderr, 'Skipping PMID:' + str(pmid) + ' in ' + args.medlineXML
					continue
				
				yearFields = elem.findall('./Article/Journal/JournalIssue/PubDate/Year')
				medlineDateFields = elem.findall('./Article/Journal/JournalIssue/PubDate/MedlineDate')

				year = None
				if len(yearFields) > 0:
					year = yearFields[0].text
				if len(medlineDateFields) > 0:
					year = medlineDateFields[0].text[0:4]
				
				year = int(year)
				
				# Let's get the appropriate file handle
				handle = None
				if year in handles:
					handle = handles[year]
				else:
					# Time to make a new one
					filename = outDir + str(year) + '.' + basenameWithoutExt + '.xml'
					handles[year] = open(filename, 'w')
					handle = handles[year]
					handle.write(header)
				
				handle.write(etree.tostring(elem).strip() + "\n")
			except:
				pmid = elem.findall('./PMID')[0].text
				print "ERROR at: "+f+"\t"+pmid
				sys.exit(255)
				
			elem.clear()

	# Tidy up and close all the handles
	for year in handles:
		handles[year].write(footer)
		handles[year].close()

	print "Completed processing:", args.medlineXML	


