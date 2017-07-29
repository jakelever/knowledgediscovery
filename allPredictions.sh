#!/bin/bash
set -euxo pipefail

optimalSV=`cat parameters.sv`
optimalThreshold=`cat parameters.threshold`

python ../analysis/calcSVDScores.py --svdU svd.all.U --svdV svd.all.V --svdSV svd.all.SV --sv $optimalSV --threshold $optimalThreshold --outFile predictions.all.txt
