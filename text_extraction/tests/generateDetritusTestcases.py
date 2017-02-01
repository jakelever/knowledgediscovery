import sys
import random
import itertools
from collections import Counter
import codecs
import argparse

if __name__ == "__main__":

	# Set a consistent seed
	random.seed(1)

	parser = argparse.ArgumentParser(description='Generate testcase files for the co-occurrence pipeline')
	
	parser.add_argument('--skeletonSentencesFile', type=argparse.FileType('r'), help='A file containing skeleton sentences with $ placeholders for terms. Must carefully not include any noun-phrases')
	parser.add_argument('--wordlistFile', type=argparse.FileType('r'), help='A file containing words to be used in the example sentences. Each line can contain multiple terms separated by |.')
	parser.add_argument('--detritusFile', type=argparse.FileType('r'), help='A file containing words to be used in the example sentences. Each line can contain multiple terms separated by |.')
	
	parser.add_argument('--outXML', type=argparse.FileType('w'), help='The output XML file containing the sentences.')
	parser.add_argument('--outDetritusCounts', type=argparse.FileType('w'), help='The output file containing the co-occurrences.')
	
	parser.add_argument('--outXML_prefix', help='The output prefix for a set of articles containing XML articles')
	
	parser.add_argument('--generateAbstracts', help='Generate an XML file containing one or more abstracts', action='store_true')
	parser.add_argument('--generateArticle', help='Generate an XML file containing a single article', action='store_true')
	parser.add_argument('--generateArticles', help='Generate a set of XML file containing a single article in each', action='store_true')
	
	parser.add_argument('--addRandomTags',  help='Add annotation tags into the text to complicate things', action='store_true')

	args = parser.parse_args()

	replaceChar = '$'

	numSentences = 400
	
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
			
	detritusDict = {}
	path = args.detritusFile.name
	args.detritusFile.close()
	with codecs.open(path, encoding='utf-8') as detritusFile:
		for i,line in enumerate(detritusFile):
			detritusTerm = line.strip()
			if not ' ' in detritusTerm:
				detritusDict[i] = detritusTerm.split('|')
	print path
			
	textBlock = []
	
	for _ in xrange(numSentences):
		thisSentence = str(random.choice(skeletonSentences))
		termIDs = []
		detritusIDs = []
		while replaceChar in thisSentence:
			
			if random.random() > 0.5: # Pick a term from the word-list
				randomID = random.choice(wordlistDict.keys())
				randomTerm = random.choice(wordlistDict[randomID])
				if randomID in termIDs:
					continue
				termIDs.append( (randomID, randomTerm) )
			else:  # Pick a detritus term
				randomID = random.choice(detritusDict.keys())
				randomTerm = random.choice(detritusDict[randomID])
				if randomID in detritusIDs:
					continue
				detritusIDs.append( (randomID, randomTerm) )
				
			thisSentence = thisSentence.replace(replaceChar, randomTerm, 1)
			
		# Capitalize the first letter of the sentence
		thisSentence = thisSentence[0].upper() + thisSentence[1:]
		
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
		detritusIDs = sorted(detritusIDs)
		textBlock.append(thisSentence.strip())
				
		if len(termIDs) > 0:
			for (detritusID,detritusTerm) in detritusIDs:
				args.outDetritusCounts.write( detritusTerm.lower() + "\n" )
	
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
