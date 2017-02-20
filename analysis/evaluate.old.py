import argparse

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

	combinedScores = [ (x,False) for x in negativeScores ] + [ (x,True) for x in positiveScores ]

	combinedScores = sorted(combinedScores)

	positiveCount = len(positiveScores)
	negativeCount = len(negativeScores)

	tp,fp = 0,0

	cb = args.classBalance
	oneMinusCB = 1.0 - cb

	thresholds = sorted(list(set(positiveScores + negativeScores)))

	# Add in one extra threshold that is the min minus one
	thresholds = [thresholds[0]-1] + thresholds

	#for threshold,trueOrFalse in combinedScores:
	#	if trueOrFalse == True:
	#		tp += 1
	#	else:
	#		fp += 1

	#	fn = positiveCount - tp
	#	tn = negativeCount - fp

	for threshold in thresholds:
		tp = sum ( [ 1 for x in positiveScores if x > threshold ] )
		fp = sum ( [ 1 for x in negativeScores if x > threshold ] )
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

