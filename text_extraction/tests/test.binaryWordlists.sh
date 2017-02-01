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
goldCooccurrences=/dev/null
goldExplanations=/dev/null

processedCooccurences1=$workingDir/processedCooccurrences1.txt
processedCooccurences2=$workingDir/processedCooccurrences2.txt
missingCooccurrences=$workingDir/missingCooccurrences.txt
extraCooccurrences=$workingDir/extraCooccurrences.txt

wordlistPickle=$workingDir/wordlist.pickle

type=generateAbstracts

generationLog=$workingDir/generationLog.txt
cooccurrenceLog=$workingDir/cooccurrenceLog.txt
picklingLog=$workingDir/picklingLog.txt
rerunLog=$workingDir/rerun.txt

echo "Generating sentences..."
python generateTestcases.py --$type --skeletonSentencesFile $skeletonSentences --wordlistFile $wordlist --outXML $goldXML  --outCooccurrences $goldCooccurrences --outExplanations $goldExplanations > $generationLog

echo "Running code..."
python ../cooccurrenceMajigger.py --termsWithSynonymsFile $wordlist --abstractsFile $goldXML --outFile $processedCooccurences1 > $cooccurrenceLog 2>&1

echo "Creating and saving wordlist..."
python ../cooccurrenceMajigger.py --termsWithSynonymsFile $wordlist --binaryTermsFile_out $wordlistPickle > $picklingLog 2>&1

echo "Rerunning with saved wordlist..."
python ../cooccurrenceMajigger.py --binaryTermsFile $wordlistPickle --abstractsFile $goldXML --outFile $processedCooccurences2 > $rerunLog 2>&1

echo "Comparing results of runs..."
comm -23 <(sort $processedCooccurences1) <(sort $processedCooccurences2) > $missingCooccurrences
comm -13 <(sort $processedCooccurences1) <(sort $processedCooccurences2) > $extraCooccurrences

numMissing=`cat $missingCooccurrences | wc -l`
numExtra=`cat $extraCooccurrences | wc -l`

failed=0

echo
echo "--------------"
echo " TEST RESULTS"
echo "--------------"

if [[ $numMissing -gt 0 ]]; then
        echo "$numMissing missing Co-Occurrences!"
        failed=1
fi

if [[ $numExtra -gt 0 ]]; then
        echo "$numExtra extra Co-Occurrences!"
        failed=1
fi

if [[ $failed -eq 0 ]]; then
        echo "Test PASSED."
        exit 0
else
        echo "Test FAILED."
        exit 255
fi
                   
