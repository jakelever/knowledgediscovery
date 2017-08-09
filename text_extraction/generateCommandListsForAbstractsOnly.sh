#!/bin/bash
set -ex

medlineAndPMCDir=$1
medlineAndPMCDir=`readlink -f $medlineAndPMCDir`

python=/gsc/software/linux-x86_64/python-2.7.2/bin/python
#python=/gsc/software/linux-x86_64-centos6/python-2.7.8/bin/python
#cooccurrenceMajigger=/projects/jlever/megaTextProject/nounphrasePipeline/cooccurrenceMajigger/cooccurrenceMajigger_articleCode.py

HERE=`pwd`

abstractCooccurencesScript=$HERE/../text_extraction/abstractCooccurrences.py
wordlist=$HERE/umlsWordlist.Final.pickle

abstractCooccurencesScript=`readlink -f $abstractCooccurencesScript`
wordlist=`readlink -f $wordlist`

# Set the directories containing the MEDLINE files and the article lists
unfilteredMedlineDir=$medlineAndPMCDir/unfilteredMedline/

mkdir -p $HERE/mined/abstracts
mkdir -p $HERE/logs/abstracts

# Create commands to extract abstracts
find $unfilteredMedlineDir -type f -name '*.xml' | sort | xargs -I FILE echo "$python $abstractCooccurencesScript --binaryTermsFile $wordlist --abstractsFile FILE --outFile $HERE/mined/abstracts/\`basename FILE\`.out > $HERE/logs/abstracts/\`basename FILE\`.out 2>&1" > commands_abstracts.txt

cat commands_abstracts.txt > commands_all.txt

tail commands_abstracts.txt > commands_mini.txt

