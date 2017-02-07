#!/bin/bash
set -ex

minedDir=$1
outDir=$2

mkdir -p $outDir/cooccurrences
mkdir -p $outDir/occurrences
mkdir -p $outDir/sentencecount

# Extract the cooccurrence,occurrence and sentencCount lines separately
find $minedDir -type f | sort | xargs -P 16 -I FILE sh -c "echo 'COOCCURRENCE FILE'; grep ^COOCCURRENCE FILE | cut -f 2- > $outDir/cooccurrences/\`basename FILE\`"
find $minedDir -type f | sort | xargs -P 16 -I FILE sh -c "echo 'OCCURRENCE FILE'; grep ^OCCURRENCE FILE | cut -f 2- > $outDir/occurrences/\`basename FILE\`"
find $minedDir -type f | sort | xargs -P 16 -I FILE sh -c "echo 'SENTENCECOUNT FILE'; grep ^SENTENCECOUNT FILE | cut -f 2- > $outDir/sentencecount/\`basename FILE\`"

