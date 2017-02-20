import argparse
import sys
import numpy as np

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Evaluate a ranking algorithm given scores for positive and negative data and generate various statistics')
	parser.add_argument('--positiveScores',required=True,type=str,help='File containing positive scores')
	parser.add_argument('--negativeScores',required=True,type=str,help='File containing negative scores')
	parser.add_argument('--classBalance',required=True,type=float,help='Fraction of data that is expected to be positive')
	parser.add_argument('--analysisName',required=True,type=str,help='Name of this analysis for output data')
	args = parser.parse_args()

	#print "Loading positive scores"
	with open(args.positiveScores) as f:
		positiveScores = [ float(line.strip()) for line in f ]
	
	#print "Loading negative scores"
	with open(args.negativeScores) as f:
		negativeScores = [ float(line.strip()) for line in f ]

	# We combined the score data with boolean to track whether its associated with a positive or negative
	# class. We then sort them by the threshold
	combinedScores = [ (x,False) for x in negativeScores ] + [ (x,True) for x in positiveScores ]
	combinedScores = sorted(combinedScores)

	positiveCount = len(positiveScores)
	negativeCount = len(negativeScores)

	#tp,fp = 0,0

	cb = args.classBalance
	oneMinusCB = 1.0 - cb

	#thresholds = sorted(list(set(positiveScores + negativeScores)))

	# First we want to find all the places that the score actually changes. These are the points where we'll calculate
	# the various scores. If the score is an integer, then there maybe multiple appeareances of the same score
	differences = [0] + [ (i+1) for i in xrange(len(combinedScores)-1) if combinedScores[i][0] != combinedScores[i+1][0] ]

	# Next we calculate an accumulating count of the number of positives and negatives as we iterate through the
	# ordered list of scores (hence we can track the increase true positives (and also false positives) as an
	# imaginary threshold is increased
	positives = [ 1 if thisClass else 0 for _,thisClass in combinedScores ]
	cumulativePositives = [0] + list(np.cumsum(positives))
	negatives = [ 1-x for x in positives ]
	cumulativeNegatives = [0] + list(np.cumsum(negatives))

	# Then we iterate through all the places where the scores change (in the ordered list)
	# Extract out the true positives and false positive count that we've already calculated
	# And then calculate the rest of the scores
	for i in differences:
		threshold = combinedScores[i][0]

		tp = cumulativePositives[i]
		fp = cumulativeNegatives[i]
		fn = positiveCount - tp
		tn = negativeCount - fp

		#precision = tp / float(tp + fp)
		true_positive_rate,false_positive_rate,adjusted_precision = 0.0,0.0,0.0

		if (tp+fn) != 0:
			true_positive_rate = tp / float(tp + fn)
		
		if (fp+tn) != 0:
			false_positive_rate = fp / float(fp + tn)

		if (tp+fp) != 0:
			adjusted_precision = (cb*tp) / (cb*tp + oneMinusCB * fp)

		adjusted_f1score = 0.0
		if (true_positive_rate+adjusted_precision) != 0.0:
			adjusted_f1score = 2 * (true_positive_rate*adjusted_precision) / (true_positive_rate+adjusted_precision)

		#print "%f\t%f\t%f\t%f\t%f" % (threshold,recall,fpr,adjustedPrecision,adjustedF1Score)
		outData = [args.analysisName, true_positive_rate, false_positive_rate, adjusted_precision, adjusted_f1score, tp, fp, tn, fn, threshold]

		line = "\t".join(map(str,outData))
		print line

