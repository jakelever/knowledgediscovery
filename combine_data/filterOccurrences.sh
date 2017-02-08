#!/bin/bash
set -ex

inData=$1
acceptableIDs=$2
outData=$3

cat $inData |\
awk -v f=$acceptableIDs -F $'\t' ' BEGIN { while (getline < f) { entities[$1]=1; } } { if ( $1 in entities ) print $0; } ' > $outData

# Sort the output
sort -k1,1n -k2,2n $outData > $outData.tmp
mv $outData.tmp $outData

