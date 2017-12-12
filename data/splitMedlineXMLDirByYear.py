import sys
import xml.etree.ElementTree as etree
import argparse
import os.path
from collections import Counter
import traceback
from datetime import date
import re

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
	parser.add_argument('--medlineXMLDir', required=True, type=existing_filepath, help='Path to a directory containing MedlineXML files')
	parser.add_argument('--pmidExclusionFile', type=existing_filepath, help='A file of PMIDs to exclude')
	parser.add_argument('--outDir', required=True, type=readable_dir, help='The output directory to store the split Medline files')
	args = parser.parse_args()
	
	header = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE MedlineCitationSet PUBLIC "-//NLM//DTD Medline Citation, 1st January, 2015//EN"\n                                    "http://www.nlm.nih.gov/databases/dtd/nlmmedlinecitationset_150101.dtd">\n<MedlineCitationSet>\n'
	footer = '</MedlineCitationSet>\n'


	pmidExclusions = {}
	if args.pmidExclusionFile:
		print "Loading PMID exclusions..."
		with open(args.pmidExclusionFile) as f:
			for line in f:
				pmid = int(line.strip())
				pmidExclusions[pmid] = True
	
	# Tidy up some paths
	medlineXMLDir = args.medlineXMLDir
	if medlineXMLDir != '/':
		medlineXMLDir += '/'
	
	outDir = args.outDir
	if outDir[-1] != '/':
		outDir += '/'

	print "Gathering file list..."
	filelist = [ filename for filename in os.listdir(medlineXMLDir) ]
	filelist = [ filename for filename in filelist if filename.endswith('.xml') ]
	filelist = sorted(filelist)

	handles = {}
	file_counts = Counter()
	citation_counts = Counter()
	MAX_PER_FILE = 30000

	for basename in filelist:
		filename = medlineXMLDir + basename
		print "Processing:", basename

		count = 0

		for event, elem in etree.iterparse(filename, events=('start', 'end', 'start-ns', 'end-ns')):
			if (event=='end' and elem.tag=='MedlineCitation'):
				count = count + 1
				if (count % 1000 == 0):
					print basename + "\t" + str(count)
				try:
					pmid = int(elem.findall('./PMID')[0].text)
					
					if pmid in pmidExclusions:
						print >> sys.stderr, 'Skipping PMID:' + str(pmid) + ' in ' + basename
						continue
					
					yearFields = elem.findall('./Article/Journal/JournalIssue/PubDate/Year')
					medlineDateFields = elem.findall('./Article/Journal/JournalIssue/PubDate/MedlineDate')

					year = None
					if len(yearFields) > 0:
						year = yearFields[0].text
					if len(medlineDateFields) > 0:
						#year = medlineDateFields[0].text[0:4]
						slashDates = re.search('\d+\/\d+\/(?P<year>\d+)',medlineDateFields[0].text)
						if slashDates:
							yearNum = int(slashDates.groupdict()['year'])
							yearCutoff = date.today().year - 1999
							if yearNum <= yearCutoff:
								year = "20%02d" % yearNum
							else:
								year = "19%02d" % yearNum
						else:
							yearSearch = re.search('([0-9]{4})', medlineDateFields[0].text)
							assert yearSearch, "Couldn't find 4 digit year in text: %s"  % medlineDateFields[0].text
							year = yearSearch.group(1)
					
					year = int(year)

					assert year >= 1800 and year <= (date.today().year+1), "Publication year (%d) must be between 1800 and next year" % year
					
					# Let's get the appropriate file handle
					handle = None
					if citation_counts[year] > MAX_PER_FILE:
						handles[year].write(footer)
						handles[year].close()
						del handles[year]

						file_counts[year] += 1
						citation_counts[year] = 0


					if year in handles:
						handle = handles[year]
					else:
						# Time to make a new one
						filename = "%s%d.%04d.xml" % (outDir,year,file_counts[year])
						handles[year] = open(filename, 'w')
						handle = handles[year]
						handle.write(header)
					
					handle.write(etree.tostring(elem).strip() + "\n")
					citation_counts[year] += 1
				except:
					pmid = elem.findall('./PMID')[0].text
					print "ERROR at: "+basename+"\t"+pmid
					print(traceback.format_exc())
					print(sys.exc_info()[0])
					sys.exit(255)
					
				elem.clear()

	# Tidy up and close all the handles
	for year in handles:
		handles[year].write(footer)
		handles[year].close()

	print "Completed processing"



