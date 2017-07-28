import argparse
import sys
import numpy as np

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Evaluate a ranking algorithm given scores for positive and negative data and generate various statistics')
	parser.add_argument('--scores',required=True,type=str,help='File containing scores')
	parser.add_argument('--classes',required=True,type=str,help='File containing classes (0=negative,1=positive)')
	parser.add_argument('--classBalance',required=True,type=float,help='Fraction of data that is expected to be positive')
	parser.add_argument('--analysisName',required=True,type=str,help='Name of this analysis for output data')
	args = parser.parse_args()

	# Get the class balance
	cb = args.classBalance
	oneMinusCB = 1.0 - cb

	# Load the scores
	with open(args.scores) as f:
		scores = [ float(line.strip()) for line in f ]
	with open(args.classes) as f:
		classes = [ int(line.strip()) for line in f ]
		assert min(classes) == 0 and max(classes) == 1, 'Classes file must be a set of binary values (0 or 1) denoting classes'

		# Turn them into boolean balues
		classes = [ bool(c) for c in classes ]

	positiveCount = sum(classes)
	negativeCount = len(classes) - positiveCount
	positiveNegativeRatio = float(positiveCount) / float(negativeCount)

	# We combined the score data with boolean to track whether its associated with a positive or negative
	# class. We then sort them by the threshold
	# Note that we sort in reverse.
	combinedScores = list(zip(scores,classes))
	combinedScores = sorted(combinedScores,reverse=True)

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
	
	# We need to add one more to pick up the last point
	differences.append(len(combinedScores))
	combinedScores.append((combinedScores[-1][0]-1,None))

	# Then we iterate through all the places where the scores change (in the ordered list)
	# Extract out the true positives and false positive count that we've already calculated
	# And then calculate the rest of the scores
	for i in differences:
		threshold = combinedScores[i][0]

		tp = cumulativePositives[i]
		fp = cumulativeNegatives[i]
		fn = positiveCount - tp
		tn = negativeCount - fp

		true_positive_rate,false_positive_rate,adjusted_precision = 0.0,0.0,0.0

		if (tp+fn) != 0:
			true_positive_rate = tp / float(tp + fn)
		
		if (fp+tn) != 0:
			false_positive_rate = fp / float(fp + tn)

		if (tp+fp) != 0:
			adjusted_precision = (cb*tp) / (cb*tp + oneMinusCB * positiveNegativeRatio * fp)

		adjusted_f1score = 0.0
		if (true_positive_rate+adjusted_precision) != 0.0:
			adjusted_f1score = 2 * (true_positive_rate*adjusted_precision) / (true_positive_rate+adjusted_precision)

		#print "%f\t%f\t%f\t%f\t%f" % (threshold,recall,fpr,adjustedPrecision,adjustedF1Score)
		outData = [args.analysisName, true_positive_rate, false_positive_rate, adjusted_precision, adjusted_f1score, tp, fp, tn, fn, threshold]

		line = "\t".join(map(str,outData))
		print line

