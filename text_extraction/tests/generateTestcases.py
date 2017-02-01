import sys
import random
import itertools
from collections import Counter
import codecs
import argparse
import unicodedata
import string
import cgi

unicodeControlChars = []

def generateUnicodeControlList():
	global unicodeControlChars
	for c in range(0x0000, 0xFFFF):
		ch = unichr(c)
		if unicodedata.category(ch)[0]=="C" and unicodedata.name(ch,"") != "":
			unicodeControlChars.append(ch)

def getRandomUnicodeControlChar():
	global unicodeControlChars
	return random.choice(unicodeControlChars)

if __name__ == "__main__":

	# Set a consistent seed
	random.seed(1)
	generateUnicodeControlList()

	parser = argparse.ArgumentParser(description='Generate testcase files for the co-occurrence pipeline')
	
	parser.add_argument('--skeletonSentencesFile', type=argparse.FileType('r'), help='A file containing skeleton sentences with $ placeholders for terms')
	parser.add_argument('--wordlistFile', type=argparse.FileType('r'), help='A file containing words to be used in the example sentences. Each line can contain multiple terms separated by |.')
	
	parser.add_argument('--outXML', type=argparse.FileType('w'), help='The output XML file containing the sentences.')
	parser.add_argument('--outCooccurrences', type=argparse.FileType('w'), help='The output file containing the co-occurrences.')
	parser.add_argument('--outExplanations', type=argparse.FileType('w'), help='The output file containing "explanations" for each co-occurrence for debugging purposes.')
	
	parser.add_argument('--outXML_prefix', help='The output prefix for a set of articles containing XML articles')
	
	parser.add_argument('--generateAbstracts', help='Generate an XML file containing one or more abstracts', action='store_true')
	parser.add_argument('--generateArticle', help='Generate an XML file containing a single article', action='store_true')
	parser.add_argument('--generateArticles', help='Generate a set of XML file containing a single article in each', action='store_true')
	
	parser.add_argument('--addRandomTags',  help='Add annotation tags into the text to complicate things', action='store_true')
	parser.add_argument('--addRandomCommandChars',  help='Add random unicode command characters into the middle of sentences', action='store_true')
	parser.add_argument('--nonsenseSentences',  help='Generate nonsense sentences with blocks of nucleotides or just random text but no spaces', action='store_true')

	args = parser.parse_args()


	textBlock = []
	
	if args.nonsenseSentences:
		numSentences = 40
		assert args.outCooccurrences is None, "Expecting outCooccurrences to NOT be set (for nonsense sentence mode)"
		assert args.outExplanations is None, "Expecting outCooccurrences to NOT be set (for nonsense sentence mode)"
		
		for _ in xrange(numSentences):
			sentenceLength = random.randint(1000,2000)
			if random.random() > 0.5: # Create a nucleotide specific sentence
				chars = [ random.choice('ACGTacgt') for _ in xrange(sentenceLength) ]
			else: # Create a random block of letters and characters (but no spaces)
				chars = [ random.choice(string.letters + string.digits + string.punctuation) for _ in xrange(sentenceLength) ]
				
			sentence = "".join(chars)
			
			# Let's escape all the nasty characters
			sentence = cgi.escape(sentence)
			
			# And let's put this sentence inside it's own paragraph.
			sentence = "<p>" + sentence + "</p>"
			
			for whitespaceChar in string.whitespace:
				assert not whitespaceChar in sentence, "The whitespace character " + unicodedata.name(unicode(whitespaceChar)) + " should not be in the auto-generated nonsense sentence"
	
			textBlock.append(sentence.strip())
				
	else:
		numSentences = 400
		assert not args.outCooccurrences is None, "Expecting outCooccurrences to be set (for normal text generation mode)"
		assert not args.outExplanations is None, "Expecting outCooccurrences to be set (for normal text generation mode)"
	
		replaceChar = '$'
		
		skeletonSentences = []	
		path = args.skeletonSentencesFile.name
		args.skeletonSentencesFile.close()
		with codecs.open(path, encoding='utf-8') as skeletonSentencesFile:
			for line in skeletonSentencesFile:
				skeletonSentences.append(line.strip())
				
		wordlistDict = {}
		path = args.wordlistFile.name
		args.wordlistFile.close()
		with codecs.open(path, encoding='utf-8') as wordlistFile:
			for i,line in enumerate(wordlistFile):
				wordlistDict[i] = line.strip().split('|')
		
		path = args.outExplanations.name
		args.outExplanations.close()
		with codecs.open(path, mode='w', encoding='utf-8') as outExplanations:
			for _ in xrange(numSentences):
				thisSentence = str(random.choice(skeletonSentences))
				termIDs = []
				while replaceChar in thisSentence:
					randomTermID = random.choice(wordlistDict.keys())
					randomTerm = random.choice(wordlistDict[randomTermID])
					if randomTermID in termIDs:
						continue
						
					termIDs.append( (randomTermID, randomTerm) )
					thisSentence = thisSentence.replace(replaceChar, randomTerm, 1)
					
				# Capitalize the first letter of the sentence
				thisSentence = thisSentence[0].upper() + thisSentence[1:]
				
				if args.addRandomCommandChars:
					while random.random() < 0.5:
						pos = random.choice(range(len(thisSentence)))
						randomChar = getRandomUnicodeControlChar() #u'\u0093'
						thisSentence = thisSentence[:pos] + randomChar + thisSentence[pos:]
					if random.random() < 0.1:
						thisSentence = u'\u2028' + thisSentence
					if random.random() < 0.1:
						thisSentence = thisSentence + u'\u2029'
					
				if args.addRandomTags:
					tokens = thisSentence.split(' ')
					pairedTags = [ ('<bold>','</bold>'), ('<italic>','</italic>'), ('<underline>','</underline>') ]
					singleTags = [ '<br />' ]
					wrappingTags = [ ('<p>', '</p>'), ('<div>','</div>') ]
					if random.random() < 0.5:
						(tagS,tagE) = random.choice(pairedTags)
						start = random.choice(range(len(tokens)))
						end = random.choice(range(start,len(tokens)))
						tokens[start] = tagS + tokens[start]
						tokens[end] = tokens[end] + tagE
					if random.random() < 0.5:
						tag = random.choice(singleTags)
						pos = random.choice(range(len(tokens)))
						tokens[pos] = tokens[pos] + tag
					if random.random() < 0.5:
						(tagS,tagE) = random.choice(wrappingTags)
						pos = random.choice(range(len(tokens)))
						tokens[0] = tagS + tokens[0]
						tokens[-1] = tokens[-1] + tagE
					thisSentence = " ".join(tokens)
					
				
				termIDs = sorted(termIDs)
						
				textBlock.append(thisSentence.strip())
				for ((idA,termA),(idB,termB)) in itertools.product(termIDs,termIDs):
					if idA < idB:
						args.outCooccurrences.write( "%d\t%d\t%d\n" % (idA, idB, 1) )
						outExplanations.write("%d\t%d\t%s\t%s\t%s\n" % (idA,idB,termA,termB,thisSentence) )
	
	if args.generateArticle or args.generateAbstracts:
		path = args.outXML.name
		args.outXML.close()
		with codecs.open(path, mode='w', encoding='utf-8') as outXML:
			if args.generateArticle:
				#./front/article-meta/title-group/article-title
				#./front/article-meta/abstract
				title = textBlock[0]
				abstractBlock = textBlock[1:(numSentences/2)]
				articleBlock = textBlock[(numSentences/2):]
				
				outXML.write('<article>\n')
				outXML.write('<front><article-meta>\n')
				outXML.write('<title-group><article-title>\n')
				outXML.write(title + '\n')
				outXML.write('</article-title></title-group>\n')
				outXML.write('<abstract>\n')
				outXML.write(" ".join(abstractBlock) + '\n')
				outXML.write('</abstract>\n')
				outXML.write('</article-meta></front>\n')
				outXML.write('<body>\n')
				outXML.write(" ".join(articleBlock) + '\n')
				outXML.write('</body>\n')
				outXML.write('</article>\n')
			elif args.generateAbstracts:
				outXML.write('<MedlineCitationSet>\n')
				textBlocksInTwos = zip(textBlock[0::2],textBlock[1::2])
				for i, (t1,t2) in enumerate(textBlocksInTwos):
					outXML.write('<MedlineCitation>\n')
					outXML.write('<PMID>' + str(i).zfill(6) + '</PMID>\n')
					outXML.write('<Article>\n')
					outXML.write('<ArticleTitle>\n')
					outXML.write(t1 + '\n')
					outXML.write('</ArticleTitle>\n')
					outXML.write('<Abstract>\n')
					outXML.write('<AbstractText>\n')
					outXML.write(t2 + '\n')
					outXML.write('</AbstractText>\n')
					outXML.write('</Abstract>\n')
					outXML.write('</Article>\n')
					outXML.write('</MedlineCitation>\n')
				outXML.write('</MedlineCitationSet>\n')
			else:
				raise Exception('Input Error', 'Expected --generateArticle, --generateArticles or --generateAbstracts')
	elif args.generateArticles:
		textBlocksInFours = zip(textBlock[0::4],textBlock[1::4],textBlock[2::4],textBlock[3::4])
		for i, (t1,t2,t3,t4) in enumerate(textBlocksInFours):
			path = args.outXML_prefix + str(i).zfill(6) + '.xml'
			with codecs.open(path, mode='w', encoding='utf-8') as outXML:
				outXML.write('<article>\n')
				outXML.write('<front><article-meta>\n')
				outXML.write('<title-group><article-title>\n')
				outXML.write(t1 + '\n')
				outXML.write('</article-title></title-group>\n')
				outXML.write('<abstract>\n')
				outXML.write(t2 + '\n')
				outXML.write('</abstract>\n')
				outXML.write('</article-meta></front>\n')
				outXML.write('<body>\n')
				outXML.write(t3 + ' ' + t4 + '\n')
				outXML.write('</body>\n')
				outXML.write('</article>\n')
	else:
		raise Exception('Input Error', 'Expected --generateArticle, --generateArticles or --generateAbstracts')
		
		
			
	
	print "Test data generation complete."
