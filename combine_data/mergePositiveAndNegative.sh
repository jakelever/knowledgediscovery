#!/bin/bash
set -euxo pipefail

inPositiveData=$1
inNegativeData=$2
outCoords=$3
outClasses=$4

# We extract the coordinates from the negative and positive data and combine along with the class info (0 or 1)
awk ' { print $1"\t"$2"\t"0; }' $inNegativeData > tmp.combined
awk ' { print $1"\t"$2"\t"1; }' $inPositiveData >> tmp.combined

# We sort by the coordinates
sort -k1,1n -k2,2n tmp.combined > tmp.sorted

# Then we extract the coordinates and classes to separate files
cut -f 1,2 tmp.sorted > $outCoords
cut -f 3 tmp.sorted > $outClasses

# And we do some clean up
rm tmp.combined tmp.sorted

