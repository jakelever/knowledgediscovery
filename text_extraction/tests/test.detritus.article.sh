#!/bin/bash
set -e
#set -x

echo "Starting test..."

workingDir=tmp
mkdir -p $workingDir
rm -f $workingDir/*

skeletonSentences=testData/skeletonSentences.detritus.txt
wordlist=testData/wordlist.unicode.txt
detritusWordlist=testData/wordlist.ascii.txt

goldXML=$workingDir/gold.xml
goldDetritus=$workingDir/gold.goldDetritus.txt

processedDetritus=$workingDir/processedDetritus.txt
missingDetritus=$workingDir/missingDetritus.txt
extraDetritus=$workingDir/extraDetritus.txt

type=generateArticle

generationLog=$workingDir/generationLog.txt
detritusLog=$workingDir/detritusLog.txt

echo "Generating test data..."
python generateDetritusTestcases.py --$type --skeletonSentencesFile $skeletonSentences --wordlistFile $wordlist --detritusFile $detritusWordlist --outXML $goldXML  --outDetritusCounts $goldDetritus > $generationLog
if [[ $? -ne 0 ]]; then
        echo "generateDetritusTestcases.py FAILED."
        echo "Quitting test early!"
        exit 255
fi

echo "Running code..."
python ../detritusMajigger.py --termsWithSynonymsFile $wordlist --articleFile $goldXML --outFile $processedDetritus > $detritusLog 2>&1
if [[ $? -ne 0 ]]; then
        echo "detritusMajigger.py FAILED."
        echo "Quitting test early!"
        exit 255
fi

comm -23 <(sort $goldDetritus) <(sort $processedDetritus) > $missingDetritus
comm -13 <(sort $goldDetritus) <(sort $processedDetritus) > $extraDetritus

numMissing=`cat $missingDetritus | wc -l`
numExtra=`cat $extraDetritus | wc -l`

failed=0

echo
echo "--------------"
echo " TEST RESULTS"
echo "--------------"

if [[ $numMissing -gt 0 ]]; then
	echo "$numMissing missing detritus!"
	failed=1
fi

if [[ $numExtra -gt 0 ]]; then
	echo "$numExtra extra detritus!"
	failed=1
fi

if [[ $failed -eq 0 ]]; then
	echo "Test PASSED."
	exit 0
else
	echo "Test FAILED."
	exit 255
fi
