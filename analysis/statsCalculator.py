import sys
import numpy as np
import argparse
import math
from collections import defaultdict
import sklearn.metrics

if __name__ == "__main__":

	# Set up the command line arguments
	parser = argparse.ArgumentParser(description='Calculate statistics on the output of the evaluation script')
	parser.add_argument('--evaluationFile', required=True, type=argparse.FileType('r'), help='The evaluation file to process')
	args = parser.parse_args()
	
	# This will hold tuples of (recall,precision) data from the file
	prPoints = defaultdict(list)
	
	# Load the evaluation file and extract the precision and recall
	for line in args.evaluationFile:
		# Skip comment rows
		if line[0] == '%' or line[0] == '#':
			continue
		
		# Extract the variable from each line of the tab-delimited file
		analysis_name, true_positive_rate, false_positive_rate, precision, f1Score, tp, fp, tn, fn, threshold = line.strip().split('\t')
		
		# Let's look at recall (TPR) and precision
		true_positive_rate = float(true_positive_rate)
		precision = float(precision)
		
		# Basic asserts to make sure that TPR and precision are numerical non-NaNs
		assert not math.isnan(true_positive_rate), "Expecting true_positive_rate to not be NaN"
		assert not math.isnan(precision), "Expecting precision to not be NaN"
		
		# Save the curve point
		prPoints[analysis_name].append((true_positive_rate,precision))
		
		
	for analysis_name in prPoints:
		# Sort the curve points
		curPoints = sorted(prPoints[analysis_name], reverse=True)
			
		# Add the graph points in bottom left and right
		curPoints = curPoints + [(0,1)]
			
		# Pull out recall and precision points separately (for numpy call)
		recalls = [ r for (r,_) in curPoints ]
		precisions = [ p for (_,p) in curPoints ]
		
		# Calculate the area using the trapezium rule	
		areaUnderPRCurve = sklearn.metrics.auc(recalls, precisions)
		
		# Just check that NaN hasn't been returned
		assert not math.isnan(areaUnderPRCurve), "Expecting areaUnderPRCurve to not be NaN"

		# Output to the terminal
		print "%s\tArea_Under_Precision_Recall_Curve:\t%f" % (analysis_name, areaUnderPRCurve)
