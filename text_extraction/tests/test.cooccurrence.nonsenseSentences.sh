#!/bin/bash

echo "Starting test..."

workingDir=tmp
mkdir -p $workingDir
rm -f $workingDir/*

wordlist=testData/wordlist.ascii.txt

goldXML=$workingDir/gold.xml

processedCooccurences=$workingDir/processedCooccurrences.txt

type=generateArticle

generationLog=$workingDir/generationLog.txt
cooccurrenceLog=$workingDir/cooccurrenceLog.txt

echo "Generating test data..."
python generateTestcases.py --$type --nonsenseSentences --outXML $goldXML  > $generationLog
if [[ $? -ne 0 ]]; then
	echo "generateTestcases.py FAILED."
	echo "Quitting test early!"
	exit 255
fi

echo "Running code..."
python ../cooccurrenceMajigger.py --termsWithSynonymsFile $wordlist --articleFile $goldXML --outFile $processedCooccurences > $cooccurrenceLog 2>&1
escapeCode=$?
if [[ $escapeCode -ne 0 ]]; then
	failed=1
	echo "cooccurrenceMajigger.py CRASHED."
else
	failed=0
fi

echo
echo "--------------"
echo " TEST RESULTS"
echo "--------------"

if [[ $failed -eq 0 ]]; then
	echo "Test PASSED."
	exit 0
else
	echo "Test FAILED."
	exit 255
fi
