#!/bin/bash
set -e
#set -x

echo "Starting test..."

workingDir=tmp
mkdir -p $workingDir
rm -f $workingDir/*

skeletonSentences=testData/skeletonSentences.txt
wordlist=testData/wordlist.ascii.txt

goldXML=$workingDir/gold.xml
goldCooccurrences=$workingDir/gold.goldCooccurrences.txt
goldExplanations=$workingDir/gold.explanations.txt

processedCooccurences=$workingDir/processedCooccurrences.txt
missingCooccurrences=$workingDir/missingCooccurrences.txt
extraCooccurrences=$workingDir/extraCooccurrences.txt

type=generateArticle

generationLog=$workingDir/generationLog.txt
cooccurrenceLog=$workingDir/cooccurrenceLog.txt

echo "Generating test data..."
python generateTestcases.py --$type --skeletonSentencesFile $skeletonSentences --wordlistFile $wordlist --outXML $goldXML  --outCooccurrences $goldCooccurrences --outExplanations $goldExplanations --addRandomTags > $generationLog

echo "Running code..."
python ../cooccurrenceMajigger.py --termsWithSynonymsFile $wordlist --articleFile $goldXML --outFile $processedCooccurences > $cooccurrenceLog 2>&1

comm -23 <(sort $goldCooccurrences) <(sort $processedCooccurences) > $missingCooccurrences
comm -13 <(sort $goldCooccurrences) <(sort $processedCooccurences) > $extraCooccurrences

numMissing=`cat $missingCooccurrences | wc -l`
numExtra=`cat $extraCooccurrences | wc -l`

failed=0

echo
echo "--------------"
echo " TEST RESULTS"
echo "--------------"

if [[ $numMissing -gt 0 ]]; then
	echo "Missing Co-Occurrences:"
	grep -F -f <(cut -f 1,2 -d $'\t' $missingCooccurrences) $goldExplanations
	failed=1
fi

if [[ $numExtra -gt 0 ]]; then
	echo "Extra Co-Occurrences:"
	cat $extraCooccurrences
	failed=1
fi

if [[ $failed -eq 0 ]]; then
	echo "Test PASSED."
	exit 0
else
	echo "Test FAILED."
	exit 255
fi
