#!/bin/bash
set -euxo pipefail

paste combinedData.testing.classes scores.testing.svd <(cut -f 6 scores.testing.other) | awk -v f=umlsWordlist.WithIDs.txt -v mappingFile=cuidMapping.txt ' BEGIN {a=0; while(getline<f) lookup[a++] = $1; while(getline<mappingFile) mapping[$1] = $3; } { cuid1=lookup[$2]; cuid2=lookup[$3]; print $0"\t"cuid1"\t"cuid2"\t"mapping[cuid1]"\t"mapping[cuid2]; } ' > explanationData.txt

# Best SVD
sort -k4,4gr explanationData.txt | head

# Worst Arrowsmith (still SVD)
awk -v threshold=$optimalThreshold ' { if ($4>threshold) print } ' explanationData.txt | sort -k5,5g | head

arrowsmithThreshold=`cat thresholds.arrowsmith.txt`
awk -v threshold=$arrowsmithThreshold ' { if ($5>threshold) print } ' explanationData.txt | sort -k4,4g | head

awk ' { if ($1==0) print } ' explanationData.txt | sort -k4,4gr | head

