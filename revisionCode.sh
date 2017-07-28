#!/bin/bash
set -euxo pipefail

validation_termCount=`cat finalDataset/training.ids | wc -l`
validation_knownCount=`cat finalDataset/training.cooccurrences | wc -l`
validation_testCount=`cat finalDataset/validation.cooccurrences | wc -l`
validation_classBalance=`echo "$validation_testCount / (($validation_termCount*($validation_termCount+1)/2) - $validation_knownCount)" | bc -l`

optimalSV=`cat parameters.sv`
optimalThreshold=`cat parameters.threshold`

../anniVectors/generateAnniVectors --cooccurrenceData finalDataset/training.cooccurrences --occurrenceData finalDataset/training.occurrences --sentenceCount `cat finalDataset/training.sentenceCounts` --vectorsToCalculate finalDataset/training.ids --outIndexFile anni.training.index --outVectorFile anni.training.vectors

python ../analysis/ScoreImplicitRelations.py --cooccurrenceFile finalDataset/training.cooccurrences --occurrenceFile finalDataset/training.occurrences --sentenceCount finalDataset/training.sentenceCounts --relationsToScore combinedData.validation.coords --anniVectors anni.training.vectors --anniVectorsIndex anni.training.index --outFile scores.validation.other

echo factaPlus > otherMethods.txt
echo bitola >> otherMethods.txt
echo anni >> otherMethods.txt
echo arrowsmith >> otherMethods.txt
echo jaccard >> otherMethods.txt
echo preferentialAttachment >> otherMethods.txt
echo amw >> otherMethods.txt
echo ltc-amw >> otherMethods.txt

col=3
while read method
do
	method=`echo $method`
	
	python ../analysis/evaluate.py --scores <(cut -f $col scores.validation.other) --classes combinedData.validation.classes --classBalance $validation_classBalance --analysisName $method > results.otherMethods.$method.txt
	
	sort -k5,5g results.otherMethods.$method.txt | cut -f 10 -d $'\t' | tail -n 1 > thresholds.$method.txt
	
	thresholdForThisMethod=`cat thresholds.$method.txt`
	
	# $9==1 && 
	paste scores.testing.other combinedData.testing.classes | awk -v threshold=$thresholdForThisMethod -v col=$col -v method=$method ' { if ($col > threshold) print method"\t"$1"_"$2; } ' >> predictioncomparison.txt
	
	col=$(($col+1))
done < otherMethods.txt

# We're looking at prediction overlap - not necessarily correct prediction overlap. Or are we? $4==1 && 
paste scores.testing.svd combinedData.testing.classes  | awk -v threshold=$optimalThreshold ' { if ($3 > threshold) print "svd\t"$1"_"$2; } ' >> predictioncomparison.txt

