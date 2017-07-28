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

from scipy.stats import hmean,gmean

def D_max(v,w,cooccurrences,occurrences):
	p1 = cooccurrences[(v,w)] / float(occurrences[v])
	p2 = cooccurrences[(v,w)] / float(occurrences[w])
	return max(p1,p2)

def D_min(v,w,cooccurrences,occurrences):
	p1 = cooccurrences[(v,w)] / float(occurrences[v])
	p2 = cooccurrences[(v,w)] / float(occurrences[w])
	return min(p1,p2)

def D_mean(v,w,cooccurrences,occurrences):
	p1 = cooccurrences[(v,w)] / float(occurrences[v])
	p2 = cooccurrences[(v,w)] / float(occurrences[w])
	return np.mean([p1,p2])

def D_hmean(v,w,cooccurrences,occurrences):
	p1 = cooccurrences[(v,w)] / float(occurrences[v])
	p2 = cooccurrences[(v,w)] / float(occurrences[w])
	return hmean([p1,p2])

def D_gmean(v,w,cooccurrences,occurrences):
	p1 = cooccurrences[(v,w)] / float(occurrences[v])
	p2 = cooccurrences[(v,w)] / float(occurrences[w])
	return gmean([p1,p2])

def calculateFactaPlusScore(x,z,neighbours,cooccurrences,occurrences,Dfunc):
	shared = neighbours[x].intersection(neighbours[z])
	product = 1.0
	for y in shared:
		tmp = 1.0 - Dfunc(x,y,cooccurrences,occurrences) * Dfunc(y,z,cooccurrences,occurrences)
		product *= tmp
	return 1.0 - product

def calculateFactaPlusScore_All(x,z,neighbours,cooccurrences,occurrences):
	shared = neighbours[x].intersection(neighbours[z])
	prod_max,prod_min,prod_mean,prod_hmean,prod_gmean = 1.0,1.0,1.0,1.0,1.0
	for y in shared:
		pxy1 = cooccurrences[(x,y)] / float(occurrences[x])
		pxy2 = cooccurrences[(x,y)] / float(occurrences[y])
		pyz1 = cooccurrences[(y,z)] / float(occurrences[y])
		pyz2 = cooccurrences[(y,z)] / float(occurrences[z])

		#tmp = 1.0 - Dfunc(x,y,cooccurrences,occurrences) * Dfunc(y,z,cooccurrences,occurrences)
		#product *= tmp

		prod_min   *= 1.0 - min(pxy1,pxy2)*min(pyz1,pyz2)
		prod_max   *= 1.0 - max(pxy1,pxy2)*max(pyz1,pyz2)
		prod_mean  *= 1.0 - np.mean([pxy1,pxy2])*np.mean([pyz1,pyz2])
		prod_hmean *= 1.0 - hmean([pxy1,pxy2])*hmean([pyz1,pyz2])
		prod_gmean *= 1.0 - gmean([pxy1,pxy2])*gmean([pyz1,pyz2])

	return (1.0-prod_min),(1.0-prod_max),(1.0-prod_mean),(1.0-prod_hmean),(1.0-prod_gmean)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Calculate scores for a set of scores')
	parser.add_argument('--cooccurrenceFile',type=str,required=True,help='File containing cooccurrences')
	parser.add_argument('--occurrenceFile',type=str,required=True,help='File containing occurrences')
	parser.add_argument('--sentenceCount',type=str,required=True,help='File containing sentence count')
	parser.add_argument('--relationsToScore',type=str,required=True,help='File containing relations to score')
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

	print "Scoring..."
	with open(args.outFile,'w') as outF:
		for i,(x,z) in enumerate(relationsToScore):
			if (i%10000) == 0:
				print i
			#facta_min = calculateFactaPlusScore(x,z,neighbours,cooccurrences,occurrences,D_min)
			#facta_max = calculateFactaPlusScore(x,z,neighbours,cooccurrences,occurrences,D_max)
			#facta_mean = calculateFactaPlusScore(x,z,neighbours,cooccurrences,occurrences,D_mean)
			#facta_hmean = calculateFactaPlusScore(x,z,neighbours,cooccurrences,occurrences,D_hmean)
			#facta_gmean = calculateFactaPlusScore(x,z,neighbours,cooccurrences,occurrences,D_gmean)

			facta_min,facta_max,facta_mean,facta_hmean,facta_gmean = calculateFactaPlusScore_All(x,z,neighbours,cooccurrences,occurrences)
			
			outData = [x,z,facta_min,facta_max,facta_mean,facta_hmean,facta_gmean]
			outLine = "\t".join(map(str,outData))
			outF.write(outLine+"\n")

	print "Completed scoring"
	print "Output to %s" % args.outFile

