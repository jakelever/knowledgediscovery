#!/bin/bash
set -ex

medlineAndPMCDir=$1
medlineAndPMCDir=`readlink -f $medlineAndPMCDir`

python=/gsc/software/linux-x86_64/python-2.7.2/bin/python
#python=/gsc/software/linux-x86_64-centos6/python-2.7.8/bin/python
#cooccurrenceMajigger=/projects/jlever/megaTextProject/nounphrasePipeline/cooccurrenceMajigger/cooccurrenceMajigger_articleCode.py

HERE=`pwd`

cooccurrenceMajigger=$HERE/../text_extraction/cooccurrenceMajigger.py
wordlist=$HERE/umlsWordlist.Final.pickle

cooccurrenceMajigger=`readlink -f $cooccurrenceMajigger`
wordlist=`readlink -f $wordlist`

# Set the directories containing the MEDLINE files and the article lists
filteredMedlineDir=$medlineAndPMCDir/filteredMedline/
articleListDir=$medlineAndPMCDir/articleLists

mkdir -p $HERE/mined/abstracts
mkdir -p $HERE/mined/articles
mkdir -p $HERE/logs/abstracts
mkdir -p $HERE/logs/articles

# Create commands to extract abstracts
find $filteredMedlineDir -type f -name '*.xml' | sort | xargs -I FILE echo "$python $cooccurrenceMajigger --binaryTermsFile $wordlist --abstractsFile FILE --outFile $HERE/mined/abstracts/\`basename FILE\`.out > $HERE/logs/abstracts/\`basename FILE\`.out 2>&1" > commands_abstracts.txt

# Create commands to extract articles
find $articleListDir -type f | sort | xargs -I FILE echo "$python $cooccurrenceMajigger --binaryTermsFile $wordlist --articleFilelist FILE --outFile $HERE/mined/articles/\`basename FILE\`.out > $HERE/logs/articles/\`basename FILE\`.out 2>&1" > commands_articles.txt

cat commands_abstracts.txt commands_articles.txt > commands_all.txt

tail commands_abstracts.txt > commands_mini.txt
tail commands_articles.txt >> commands_mini.txt

