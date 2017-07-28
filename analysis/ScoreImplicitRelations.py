import argparse
from math import log
from collections import defaultdict

from multiprocessing import Pool,Manager
from functools import partial
from contextlib import closing
import time
import logging
import sys
import numpy as np

def D(v,w,cooccurrences,occurrences):
	p1 = cooccurrences[(v,w)] / float(occurrences[v])
	p2 = cooccurrences[(v,w)] / float(occurrences[w])
	return max(p1,p2)

def calculateFactaPlusScore(x,z,neighbours,cooccurrences,occurrences):
	shared = neighbours[x].intersection(neighbours[z])
	product = 1.0
	for y in shared:
		tmp = 1.0 - D(x,y,cooccurrences,occurrences) * D(y,z,cooccurrences,occurrences)
		product *= tmp
	return 1.0 - product

def calculateAverageMinimumWeight(x,z,neighbours,cooccurrences,occurrences):
	shared = neighbours[x].intersection(neighbours[z])
	if len(shared) == 0:
		return 0

	total = 0.0
	for y in shared:
		total += min(cooccurrences[(x,y)],cooccurrences[(y,z)])
	return total / float(len(shared))

def calculateLinkingTermCountwithAMW(x,z,neighbours,cooccurrences,occurrences):
	linkingTermCount = calculateArrowsmithScore(x,z,neighbours,cooccurrences,occurrences)
	amw = calculateAverageMinimumWeight(x,z,neighbours,cooccurrences,occurrences)

	# In order to sort by LTC then by AMW, we simply scale up the LTC term in comparison to AMW (only works if AMW is less than 1000)
	return linkingTermCount + 0.001 * amw

def calculateBitolaScore(x,z,neighbours,cooccurrences,occurrences):
	shared = neighbours[x].intersection(neighbours[z])
	total = 0
	for y in shared:
		total += cooccurrences[(x,y)] * cooccurrences[(y,z)]
	return total

def calculateArrowsmithScore(x,z,neighbours,cooccurrences,occurrences):
	shared = neighbours[x].intersection(neighbours[z])
	return len(shared)

def calculateJaccardIndex(x,z,neighbours,cooccurrences,occurrences):
	shared = neighbours[x].intersection(neighbours[z])
	combined = neighbours[x].union(neighbours[z])
	return len(shared)/float(len(combined))

def calculatePreferentialAttachment(x,z,neighbours,cooccurrences,occurrences):
	score = len(neighbours[x]) + len(neighbours[z])
	return score
				
def calculateANNIScore(x,z,conceptVectorsIndex,conceptVectors):
	indexX = conceptVectorsIndex[x]
	indexZ = conceptVectorsIndex[z]
	
	vectorX = conceptVectors[indexX,:]
	vectorZ = conceptVectors[indexZ,:]
	dotprod = np.dot(vectorX,vectorZ)
	#entities = vectorX.keys().intersection(vectorZ.keys())
	#dotprod = sum( [ vectorX[e]*vectorZ[e] for e in entities ] )
	#assert len(vectorX) == len(vectorZ)
	#dotprod = sum( [ i*j for i,j in zip(vectorX,vectorZ) ] )
	return dotprod

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Calculate scores for a set of scores')
	parser.add_argument('--cooccurrenceFile',type=str,required=True,help='File containing cooccurrences')
	parser.add_argument('--occurrenceFile',type=str,required=True,help='File containing occurrences')
	parser.add_argument('--sentenceCount',type=str,required=True,help='File containing sentence count')
	parser.add_argument('--relationsToScore',type=str,required=True,help='File containing relations to score')
	parser.add_argument('--anniVectors',type=str,help='File containing the raw ANNI vector data')
	parser.add_argument('--anniVectorsIndex',type=str,help='File containing the index for the ANNI vector data')
	parser.add_argument('--outFile',type=str,required=True,help='File to output scores to')

	args = parser.parse_args()

	print "Loading relationsToScore"
	relationsToScore = []
	entitiesToScore = set()
	with open(args.relationsToScore) as f:
		for line in f:
			split = map(int,line.strip().split())
			x,y = split[:2]
			relationsToScore.append((x,y))
			entitiesToScore.add(x)
			entitiesToScore.add(y)
	entitiesToScore = sorted(list(entitiesToScore))
	print "Loaded relationsToScore"

	print "Loading sentenceCount"
	sentenceCount = None
	with open(args.sentenceCount) as f:
		sentenceCount = int(f.readline().strip())
	print "Loaded sentenceCount"

	print "Loading occurrences..."
	occurrences = {}
	with open(args.occurrenceFile) as f:
		for line in f:
			x,count = map(int,line.strip().split())
			occurrences[x] = count
	print "Loaded occurrences"

	print "Loading cooccurrences..."
	cooccurrences = {}
	neighbours = defaultdict(set)
	with open(args.cooccurrenceFile) as f:
		for line in f:
			x,y,count = map(int,line.strip().split())
			cooccurrences[(x,y)] = count
			cooccurrences[(y,x)] = count
			neighbours[x].add(y)
			neighbours[y].add(x)
	print "Loaded cooccurrences"

	doANNI = args.anniVectorsIndex and args.anniVectors
	if doANNI:
		print "Loading ANNI concept vectors..."
		#anniConceptVectors = prepareANNIConceptVectors(entitiesToScore,neighbours,cooccurrences,occurrences,sentenceCount)
		with open(args.anniVectorsIndex) as f:
			anniVectorsIndex = { int(line.strip()):i for i,line in enumerate(f) }
		
		with open(args.anniVectors,'rb') as f:
			anniConceptVectors = np.fromfile(f,np.float32)
			vectorSize = int(anniConceptVectors.shape[0] / len(anniVectorsIndex))
			anniConceptVectors = anniConceptVectors.reshape((len(anniVectorsIndex),vectorSize))

			#print "Normalising ANNI concept vectors"
			#l2norm = np.sqrt((anniConceptVectors * anniConceptVectors).sum(axis=1))
			#anniConceptVectors = anniConceptVectors / l2norm.reshape(anniConceptVectors.shape[0],1)

			
		
		print "Loaded ANNI concept vectors"

	print "Scoring..."
	with open(args.outFile,'w') as outF:
		for i,(x,z) in enumerate(relationsToScore):
			if (i%10000) == 0:
				print i
			factaPlusScore = calculateFactaPlusScore(x,z,neighbours,cooccurrences,occurrences)
			bitolaScore = calculateBitolaScore(x,z,neighbours,cooccurrences,occurrences)
			arrowsmithScore = calculateArrowsmithScore(x,z,neighbours,cooccurrences,occurrences)
			jaccardScore = calculateJaccardIndex(x,z,neighbours,cooccurrences,occurrences)
			preferentialAttachmentScore = calculatePreferentialAttachment(x,z,neighbours,cooccurrences,occurrences)
		
			anniScore = -1
			if doANNI:
				anniScore = calculateANNIScore(x,z,anniVectorsIndex,anniConceptVectors)
	
			amwScore = calculateAverageMinimumWeight(x,z,neighbours,cooccurrences,occurrences)
			ltc_amwScore = calculateLinkingTermCountwithAMW(x,z,neighbours,cooccurrences,occurrences)

			assert amwScore < 1000.0, "The LTC-AMW score currently limits the AMW score to no more than 1000.0"

			outData = [x,z,factaPlusScore,bitolaScore,anniScore,arrowsmithScore,jaccardScore,preferentialAttachmentScore,amwScore,ltc_amwScore]
			outLine = "\t".join(map(str,outData))
			outF.write(outLine+"\n")

	print "Completed scoring"
	print "Output to %s" % args.outFile

