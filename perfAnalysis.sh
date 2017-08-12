#!/bin/bash
#set -euxo pipefail
set -ux

echo factaplus > perfMethods.txt
echo bitola >> perfMethods.txt
echo arrowsmith >> perfMethods.txt
echo jaccard >> perfMethods.txt
echo preferentialattachment >> perfMethods.txt
echo amw >> perfMethods.txt
echo ltc-amw >> perfMethods.txt

python=~/miniconda_install/myproject/bin/python


# Get the full number of terms in the wordlist
allTermsCount=`cat umlsWordlist.Final.txt | wc -l`

#/usr/bin/time -v bash ../analysis/runSVD.sh --dimension $allTermsCount --svNum 500 --matrix finalDataset/training.cooccurrences --outU perf.svd.training.U --outV perf.svd.training.V --outSV perf.svd.training.SV --mirror --binarize &> perf.log.svdTraining

#exit 0

/usr/bin/time -v ../anniVectors/generateAnniVectors --cooccurrenceData finalDataset/trainingAndValidation.cooccurrences --occurrenceData finalDataset/trainingAndValidation.occurrences --sentenceCount `cat finalDataset/trainingAndValidation.sentenceCounts` --vectorsToCalculate finalDataset/trainingAndValidation.ids --outIndexFile perf.anni.trainingAndValidation.index --outVectorFile perf.anni.trainingAndValidation.vectors &> perf.log.anniVectors


/usr/bin/time -v bash ../analysis/runSVD.sh --dimension $allTermsCount --svNum 500 --matrix finalDataset/training.cooccurrences --outU perf.svd.training.U --outV perf.svd.training.V --outSV perf.svd.training.SV --mirror --binarize &> perf.log.svdTraining

/usr/bin/time -v bash ../analysis/runSVD.sh --dimension $allTermsCount --svNum 500 --matrix finalDataset/trainingAndValidation.cooccurrences --outU perf.svd.trainingAndValidation.U --outV perf.svd.trainingAndValidation.V --outSV perf.svd.trainingAndValidation.SV --mirror --binarize &> perf.log.svdTrainingAndValidation

while read method
do
	/usr/bin/time -v $python ../analysis/separate/$method.py --cooccurrenceFile finalDataset/trainingAndValidation.cooccurrences --occurrenceFile finalDataset/trainingAndValidation.occurrences --sentenceCount finalDataset/trainingAndValidation.sentenceCounts --relationsToScore combinedData.testing.coords --outFile perf.out.$method &> perf.log.$method
	
done < perfMethods.txt

method=anni
/usr/bin/time -v $python ../analysis/separate/$method.py --cooccurrenceFile finalDataset/trainingAndValidation.cooccurrences --occurrenceFile finalDataset/trainingAndValidation.occurrences --sentenceCount finalDataset/trainingAndValidation.sentenceCounts --relationsToScore combinedData.testing.coords --anniVectors anni.trainingAndValidation.vectors --anniVectorsIndex anni.trainingAndValidation.index --outFile perf.out.$method &> perf.log.$method

optimalSV=`cat parameters.sv`
/usr/bin/time -v $python ../analysis/calcSVDScores.py --svdU svd.trainingAndValidation.U --svdV svd.trainingAndValidation.V --svdSV svd.trainingAndValidation.SV --relationsToScore combinedData.testing.coords --outFile perf.out.svd --sv $optimalSV &> perf.log.svd

grep 'System time' perf.log.* > perf.summary.time
grep 'Maximum resident set size' perf.log.* > perf.summary.mem



