#!/bin/bash
set -ex

inMatrix=$1
occurrences=$2
prevMatrix=$3
outMatrix=$4

cat $inMatrix |\
awk -v f=$occurrences -F $'\t' ' BEGIN { while (getline < f) { entities[$1]=1; } } { key=$1"\t"$2; if ( ($1 in entities) && ($2 in entities) ) print $0; } '  |\
awk -v f=$prevMatrix -F $'\t' ' BEGIN { while (getline < f) { rels[$1"\t"$2]=1; rels[$2"\t"$1]=1; } } { key=$1"\t"$2; if ( !(key in rels) ) print $0; } '  > $outMatrix

# Sort the output
sort -k1,1n -k2,2n $outMatrix > $outMatrix.tmp
mv $outMatrix.tmp $outMatrix

