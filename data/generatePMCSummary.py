import fnmatch
import os
import argparse
import xml.etree.cElementTree as etree
import codecs
import sys

# Remove control characters from text and some other weird stuff
def handleEncoding(text):
	# Remove some "control-like" characters (left/right separator)
	text = text.replace(u'\u2028',' ').replace(u'\u2029',' ')
	text = "".join(ch for ch in text if unicodedata.category(ch)[0]!="C")
	text = text.encode('utf8')
	return text.strip()
	
# XML elements to ignore the contents of
ignoreList = ['table', 'table-wrap', 'xref', 'disp-formula', 'inline-formula', 'ref-list', 'bio', 'ack', 'graphic', 'media', 'tex-math', 'mml:math', 'object-id', 'ext-link']

# XML elements to separate text between
separationList = ['title', 'p', 'sec', 'break', 'def-item', 'list-item', 'caption']
def extractTextFromElem(elem):
	textList = []
	
	# Extract any raw text directly in XML element or just after
	head = ""
	if elem.text:
		head = elem.text
	tail = ""
	if elem.tail:
		tail = elem.tail
	
	# Then get the text from all child XML nodes recursively
	childText = []
	for child in elem:
		childText = childText + extractTextFromElem(child)
		
	# Check if the tag should be ignore (so don't use main contents)
	if elem.tag in ignoreList:
		return [tail.strip()]
	# Add a zero delimiter if it should be separated
	elif elem.tag in separationList:
		return [0] + [head] + childText + [tail]
	# Or just use the whole text
	else:
		return [head] + childText + [tail]
	

# Merge a list of extracted text blocks and deal with the zero delimiter
def extractTextFromElemList_merge(list):
	textList = []
	current = ""
	# Basically merge a list of text, except separate into a new list
	# whenever a zero appears
	for t in list:
		if t == 0: # Zero delimiter so split
			if len(current) > 0:
				textList.append(current)
				current = ""
		else: # Just keep adding
			current = current + " " + t
			current = current.strip()
	if len(current) > 0:
		textList.append(current)
	return textList
	
# Main function that extracts text from XML element or list of XML elements
def extractTextFromElemList(elemList):
	textList = []
	# Extracts text and adds delimiters (so text is accidentally merged later)
	if isinstance(elemList, list):
		for e in elemList:
			textList = textList + extractTextFromElem(e) + [0]
	else:
		textList = extractTextFromElem(elemList) + [0]

	# Merge text blocks with awareness of zero delimiters
	mergedList = extractTextFromElemList_merge(textList)
	
	# Remove any newlines (as they can be trusted to be syntactically important)
	mergedList = [ text.replace('\n', ' ') for text in mergedList ]
	
	return mergedList
	
def summariseArticle(articleFilename, articleElem, outFile, type):
	articleLang = 'en'
	if 'xml:lang' in articleElem.attrib:
		articleLang = articleElem.attrib['xml:lang'].strip().replace('\n',' ')
	assert articleLang == 'en'

	articleType = ''
	if 'article-type' in articleElem.attrib:
		articleType = articleElem.attrib['article-type'].strip().replace('\n',' ')

	# Attempt to extract the PubMed ID, PubMed Central IDs and DOIs
	pmidText = ''
	pmcidText = ''
	doiText = ''
	article_id = articleElem.findall('./front/article-meta/article-id') + articleElem.findall('./front-stub/article-id')
	for a in article_id:
		if a.text and 'pub-id-type' in a.attrib and a.attrib['pub-id-type'] == 'pmid':
			pmidText = a.text.strip().replace('\n',' ')
		if a.text and 'pub-id-type' in a.attrib and a.attrib['pub-id-type'] == 'pmc':
			pmcidText = a.text.strip().replace('\n',' ')
		if a.text and 'pub-id-type' in a.attrib and a.attrib['pub-id-type'] == 'doi':
			doiText = a.text.strip().replace('\n',' ')
			
	# Attempt to get the publication date
	pubdates = articleElem.findall('./front/article-meta/pub-date') + articleElem.findall('./front-stub/pub-date')
	pubYear = ""
	if len(pubdates) >= 1:
		pubYear = pubdates[0].find("year").text.strip().replace('\n',' ')
	
	articleFilename = os.path.abspath(articleFilename)

	# Only print out a summary if we have a PMID or PMCID
	if pmidText != '' or pmcidText != '':
		summaryText = '%s\t%s\t%s\t%s\t%s\t%s\n' % (pmidText,pmcidText,articleType,pubYear,articleFilename,type)
		outFile.write(summaryText)

# It's the main bit. Yay!
if __name__ == '__main__':

	# From StackOverflow: http://stackoverflow.com/questions/11415570/directory-path-types-with-argparse
	def readable_dir(prospective_dir):
		if not os.path.isdir(prospective_dir):
			raise Exception('readable_dir:{0} is not a valid path'.format(prospective_dir))
		if os.access(prospective_dir, os.R_OK):
			return prospective_dir
		else:
			raise Exception('readable_dir:{0} is not a readable dir'.format(prospective_dir))

	# Arguments for the command line
	parser = argparse.ArgumentParser(description='Generates a summary file for a directory containing PubMedCentral XML files')
	parser.add_argument('--pmcDir', required=True, type=readable_dir, help='A list of terms for extraction with synonyms separated by a |')
	parser.add_argument('--outFile', required=True, type=str, help='File to output cooccurrences')

	args = parser.parse_args()
	
	with codecs.open(args.outFile, 'w', encoding='utf-8') as outFile:
		# Look for all nxml files in the pmcDir
		for root, dirnames, filenames in os.walk(args.pmcDir):
			for filename in fnmatch.filter(filenames, '*.nxml'):
				fullfilename = os.path.join(root, filename)
				for event, elem in etree.iterparse(fullfilename, events=('start', 'end', 'start-ns', 'end-ns')):
					# Skip to the article element in the file
					if (event=='end' and elem.tag=='article'):
						try:
							summariseArticle(fullfilename, elem, outFile, 'MAIN')
							
							subarticles = elem.findall('./sub-article')
							for subarticle in subarticles:
								summariseArticle(fullfilename, subarticle, outFile, 'SUB')
						except:
							print >> sys.stderr, 'ERROR with file:' + fullfilename
							raise
					
						# Less important here (compared to abstracts) as each article file is not too big
						elem.clear()
					
