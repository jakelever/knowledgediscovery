#!/bin/bash
set -euxo pipefail

cooccurrenceDir=$1
occurrenceDir=$2
sentenceCountDir=$3

outDir=$4

mkdir -p $outDir

cooccurrenceDir=`readlink -f $cooccurrenceDir`
occurrenceDir=`readlink -f $occurrenceDir`
sentenceCountDir=`readlink -f $sentenceCountDir`
outDir=`readlink -f $outDir`

tmpDir=tmp.$HOSTNAME.$$.$RANDOM
rm -fr $tmpDir

# Get directory of this script
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

###########################
# Training and Validation #
###########################

mkdir -p $tmpDir/all/cooccurrences
mkdir -p $tmpDir/all/occurrences
mkdir -p $tmpDir/all/sentenceCounts

find $cooccurrenceDir -type f | xargs -I FILE basename FILE | cut -f 1 -d '.' | sort -n -u > $tmpDir/all.years

cat $tmpDir/all.years | xargs -I YEAR echo "find $cooccurrenceDir -type f -name 'YEAR*'" | sh > $tmpDir/allFiles.cooccurrences
cat $tmpDir/all.years | xargs -I YEAR echo "find $occurrenceDir -type f -name 'YEAR*'" | sh > $tmpDir/allFiles.occurrences
cat $tmpDir/all.years | xargs -I YEAR echo "find $sentenceCountDir -type f -name 'YEAR*'" | sh > $tmpDir/allFiles.sentenceCounts

cat $tmpDir/allFiles.cooccurrences | xargs -I FILE ln -s FILE $tmpDir/all/cooccurrences/
cat $tmpDir/allFiles.occurrences | xargs -I FILE ln -s FILE $tmpDir/all/occurrences
cat $tmpDir/allFiles.sentenceCounts | xargs -I FILE ln -s FILE $tmpDir/all/sentenceCounts

bash $HERE/mergeMatrix_2keys.sh $tmpDir/all/cooccurrences/ $outDir/all.cooccurrences
bash $HERE/mergeMatrix_1key.sh $tmpDir/all/occurrences $outDir/all.occurrences.unfiltered
bash $HERE/mergeMatrix_0keys.sh $tmpDir/all/sentenceCounts $outDir/all.sentenceCounts

# Get the list of term IDs that actually occur in cooccurrences
cat $outDir/all.cooccurrences | cut -f 1,2 -d $'\t' | tr '\t' '\n' | sort -un > $outDir/all.ids

bash $HERE/filterOccurrences.sh $outDir/all.occurrences.unfiltered $outDir/all.ids $outDir/all.occurrences
rm $outDir/all.occurrences.unfiltered

python $HERE/checkFilteredOccurrences.py --occurrenceFile $outDir/all.occurrences --acceptedIDs $outDir/all.ids

rm -fr $tmpDir

