# Knowledge Discovery using Recommendation Systems

All this code WILL BE in a master script that can run the entire analysis.

## Install Dependencies

There are a few dependencies to install first. Run the following scripts and make sure they all succeeded.

```bash
cd dependencies
bash install.geniatagger.sh
bash install.powergraph.sh
bash install.lingpipe.sh
bash install.tclap.sh
cd ../
```

## Setup Lingpipe

## Compile ANNI vector generation code

Most of the analysis code is in Python and doesn't require compilation. Only the code to generate ANNI concept vectors requires compilation as it is written in C++.

```bash
cd anniVectors
make
cd ../
```

## Working Directory

We're going to do all analysis inside a working directory and call the various scripts from within it. So in the root of this repo we do the following.

```bash
mkdir workingDir
cd workingDir
```

## Download PubMed and PubMed Central

We need to download the abstracts from PubMed and full text articles from the PubMed Central Open Access subset. This is all managed by the prepareMedlineANDPMCData.sh script.

```bash
bash ../data/prepareMedlineAndPMCData.sh medlineAndPMC
```

## Install UMLS

This involves downloading UMLS from https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html and running MetamorphoSys. Install the Active dataset. Unfortunately this can't currently be done via the command line.

## Create the UMLS-based word-list

A script will pull out the necessary terms, their IDs, semantic types and synonyms from the UMLS RRF files.

```bash
bash ../data/generateUMLSWordlist.sh /projects/bioracle/ncbiData/umls/2016AB/META/ ./
```

TEMPORARY: We'll do a little simplification for the testing process. Basically we going to build a mini word-list

```bash
mv umlsWordlist.WithIDs.txt fullWordlist.WithIDs.txt
rm umlsWordlist.Final.txt

echo -e "cancer\ninib\nanib" > simpler_terms.txt
grep -f simpler_terms.txt fullWordlist.WithIDs.txt > umlsWordlist.WithIDs.txt

# Make sure Alzheimer's and Parkinson's terms are included
grep "C0002395" fullWordlist.WithIDs.txt >> umlsWordlist.WithIDs.txt
grep "C0030567" fullWordlist.WithIDs.txt >> umlsWordlist.WithIDs.txt
grep "C0030567" fullWordlist.WithIDs.txt >> umlsWordlist.WithIDs.txt

sort -u umlsWordlist.WithIDs.txt > umlsWordlist.WithIDs.txt.unique
mv umlsWordlist.WithIDs.txt.unique umlsWordlist.WithIDs.txt

cut -f 3 -d $'\t' umlsWordlist.WithIDs.txt > umlsWordlist.Final.txt
```

We then need to process this wordlist into a Python pickled file and remove stop-words and short words.

```bash
python ../text_extraction/cooccurrenceMajigger.py --termsWithSynonymsFile umlsWordlist.Final.txt --stopwordsFile ../data/selected_stopwords.txt --removeShortwords --binaryTermsFile_out umlsWordlist.Final.pickle
```

## Run text mining across all PubMed and PubMed Central

First we generate a list of commands to parse all the text files. This is for use on a cluster.

```bash
bash ../text_extraction/generateCommandLists.sh medlineAndPMC
```

Next we need to run the text mining tool on a cluster. This may need editing for your partocular environment.

```bash
bash ../text_extraction/runCommandsOnCluster.sh commands_all.txt
```

## Combine data into a dataset for analysis

We first need to extract the cooccurrences, occurrences and sentence counts from the mined data (as they're all combined in the same output files)

```bash
bash ../combine_data/splitDataTypes.sh mined mined_and_separated
```

Next up we merged these various cooccurrence, occurrence and sentence count files down into the final data set

```bash
bash ../combine_data/produceDataset.sh mined_and_separated/cooccurrences mined_and_separated/occurrences mined_and_separated/sentencecount 2010 finalDataset
```

## Generate ANNI Vectors

ANNI requires creating concept vectors for all concepts

```bash
../anniVectors/generateAnniVectors --cooccurrenceData finalDataset/trainingAndValidation.cooccurrences --occurrenceData finalDataset/trainingAndValidation.occurrences --sentenceCount `cat finalDataset/trainingAndValidation.sentenceCounts` --vectorsToCalculate finalDataset/trainingAndValidation.ids --outIndexFile anni.trainingAndValidation.index --outVectorFile anni.trainingAndValidation.vectors
```

## Generate negative data for comparison

Next we'll create negative data to allow comparison of the different ranking methods.

```bash
negativeCount=1000000
python ../analysis/generateNegativeData.py --trueData <(cat finalDataset/training.cooccurrences finalDataset/validation.cooccurrences) --knownConceptIDs finalDataset/training.ids --num $negativeCount --outFile negativeData.validation

python ../analysis/generateNegativeData.py --trueData <(cat finalDataset/trainingAndValidation.cooccurrences finalDataset/testing.all.cooccurrences) --knownConceptIDs finalDataset/trainingAndValidation.ids --num $negativeCount --outFile negativeData.testing
```

## Merge positive and negative data into one file

We'll combine the positive and negative points into one file and keep track of the classes separately

```bash
bash ../combine_data/mergePositiveAndNegative.sh finalDataset/validation.subset.1000000.cooccurrences negativeData.validation combinedData.validation.coords combinedData.validation.classes

bash ../combine_data/mergePositiveAndNegative.sh finalDataset/testing.all.subset.1000000.cooccurrences negativeData.testing combinedData.testing.coords combinedData.testing.classes
```

## Run Singular Value Decomposition

We'll run a singular value decomposition on the co-occurrence data.

```bash
# Get the full number of terms in the wordlist
allTermsCount=`cat umlsWordlist.Final.txt | wc -l`

bash ../analysis/runSVD.sh --dimension $allTermsCount --svNum 500 --matrix finalDataset/training.cooccurrences --outU svd.training.U --outV svd.training.V --outSV svd.training.SV --mirror --binarize

bash ../analysis/runSVD.sh --dimension $allTermsCount --svNum 500 --matrix finalDataset/trainingAndValidation.cooccurrences --outU svd.trainingAndValidation.U --outV svd.trainingAndValidation.V --outSV svd.trainingAndValidation.SV --mirror --binarize

bash ../analysis/runSVD.sh --dimension $allTermsCount --svNum 500 --matrix finalDataset/all.cooccurrences --outU svd.all.U --outV svd.all.V --outSV svd.all.SV --mirror --binarize
```

We first need to calculate the class balance for the validation set

```bash
validation_termCount=`cat finalDataset/training.ids | wc -l`
validation_knownCount=`cat finalDataset/training.cooccurrences | wc -l`
validation_testCount=`cat finalDataset/validation.cooccurrences | wc -l`
validation_classBalance=`echo "$validation_testCount / (($validation_termCount*($validation_termCount+1)/2) - $validation_knownCount)" | bc -l`
```

Now we need to test a range of singular values to find the optimal value

```bash
minSV=5
maxSV=500
numThreads=16

mkdir svd.crossvalidation
seq $minSV $maxSV | xargs -I NSV -P $numThreads python ../analysis/calcSVDScores.py --svdU svd.training.U --svdV svd.training.V --svdSV svd.training.SV --relationsToScore combinedData.validation.coords --sv NSV --outFile svd.crossvalidation/scores.NSV

seq $minSV $maxSV | xargs -I NSV -P $numThreads bash -c "python ../analysis/evaluate.py --scores <(cut -f 3 svd.crossvalidation/scores.NSV) --classes combinedData.validation.classes --classBalance $validation_classBalance --analysisName NSV > svd.crossvalidation/results.NSV"

cat svd.crossvalidation/results.* > svd.results
```

Then we calculate the Area under the Precision Recall curve for each # of singular values and find the optimal value

```bash
python ../analysis/statsCalculator.py --evaluationFile svd.results > curves.svd
sort -k3,3g curves.svd | tail -n 1 | cut -f 1 > parameters.sv
optimalSV=`cat parameters.sv`
```

We'll also calculate the optimal threshold which is useful later. We won't use a threshold to compare the different methods (as we're using the Area under the Precision Recall curve). But we will want to use a threshold to call positive/negatives later in our analysis. The threshold is calculated as the value that gives the optimal F1-score. So we sort by F1-score and pull out the associated threshold.

```bash
sort -k5,5g svd.crossvalidation/results.$optimalSV | cut -f 10 -d $'\t' | tail -n 1 > parameters.threshold
optimalThreshold=`cat parameters.threshold`
```

## Calculate scores for positive & negative relationships

Calculate the scores for the SVD method

```bash
python ../analysis/calcSVDScores.py --svdU svd.trainingAndValidation.U --svdV svd.trainingAndValidation.V --svdSV svd.trainingAndValidation.SV --relationsToScore combinedData.testing.coords --outFile scores.testing.svd --sv $optimalSV
```

Calculate the scores for the other methods

```bash
python ../analysis/ScoreImplicitRelations.py --cooccurrenceFile finalDataset/trainingAndValidation.cooccurrences --occurrenceFile finalDataset/trainingAndValidation.occurrences --sentenceCount finalDataset/trainingAndValidation.sentenceCounts --relationsToScore combinedData.testing.coords --anniVectors anni.trainingAndValidation.vectors --anniVectorsIndex anni.trainingAndValidation.index --outFile scores.testing.other
```

## Generate precision/recall curves for each method with associated statistics

First we need to calculate the class balance.

```bash
testing_termCount=`cat finalDataset/trainingAndValidation.ids | wc -l`
testing_knownCount=`cat finalDataset/trainingAndValidation.cooccurrences | wc -l`
testing_testCount=`cat finalDataset/testing.all.cooccurrences | wc -l`
testing_classBalance=`echo "$testing_testCount / (($testing_termCount*($testing_termCount+1)/2) - $testing_knownCount)" | bc -l`
```
Then we run evaluate on the separate columns of the score file

```bash
python ../analysis/evaluate.py --scores <(cut -f 3 scores.testing.svd) --classes combinedData.testing.classes --classBalance $testing_classBalance --analysisName "SVD_$optimalSV" >> curves.all

python ../analysis/evaluate.py --scores <(cut -f 3 scores.testing.other) --classes combinedData.testing.classes --classBalance $testing_classBalance --analysisName factaPlus >> curves.all

python ../analysis/evaluate.py --scores <(cut -f 4 scores.testing.other) --classes combinedData.testing.classes --classBalance $testing_classBalance --analysisName bitola >> curves.all

python ../analysis/evaluate.py --scores <(cut -f 5 scores.testing.other) --classes combinedData.testing.classes --classBalance $testing_classBalance --analysisName anni >> curves.all

python ../analysis/evaluate.py --scores <(cut -f 6 scores.testing.other) --classes combinedData.testing.classes --classBalance $testing_classBalance --analysisName arrowsmith >> curves.all

python ../analysis/evaluate.py --scores <(cut -f 7 scores.testing.other) --classes combinedData.testing.classes --classBalance $testing_classBalance --analysisName jaccard >> curves.all

python ../analysis/evaluate.py --scores <(cut -f 8 scores.testing.other) --classes combinedData.testing.classes --classBalance $testing_classBalance --analysisName preferentialAttachment  >> curves.all

python ../analysis/evaluate.py --scores <(cut -f 9 scores.testing.other) --classes combinedData.testing.classes --classBalance $testing_classBalance --analysisName amw  >> curves.all

python ../analysis/evaluate.py --scores <(cut -f 10 scores.testing.other) --classes combinedData.testing.classes --classBalance $testing_classBalance --analysisName ltc-amw  >> curves.all
```

Then we finally calculate the area under the precision recall curve for each method.

```bash
python ../analysis/statsCalculator.py --evaluationFile curves.all > curves.stats
```

## Calculate Predictions for Following Years

Insert explanation here

```bash
rm -f yearByYear.results
for testFile in `find finalDataset/ -name 'testing*subset*' | grep -v all | sort`
do
  testYear=`basename $testFile | cut -f 2 -d '.'`

  cooccurrenceCount=`cat $testFile | wc -l`

  python ../analysis/calcSVDScores.py --svdU svd.trainingAndValidation.U --svdV svd.trainingAndValidation.V --svdSV svd.trainingAndValidation.SV --relationsToScore $testFile --sv $optimalSV --threshold $optimalThreshold --outFile tmpPredictions

  predictionCount=`cat tmpPredictions | wc -l`

  echo -e "$testYear\t$cooccurrenceCount\t$predictionCount" >> yearByYear.results
done
```

We'll also calculate the total number of predictions made using the parameters (# singular values and threshold). This will give us a better idea of precision when making these predictions.

```bash
python ../analysis/countSVDPredictions.py --svdU svd.trainingAndValidation.U --svdV svd.trainingAndValidation.V --svdSV svd.trainingAndValidation.SV --sv $optimalSV --threshold $optimalThreshold --idsFile finalDataset/trainingAndValidation.ids --relationsToIgnore finalDataset/trainingAndValidation.cooccurrences --outFile yearByYear.predcount
```

## Plot Figures

Lastly we plot the figures used in the paper. The first is a comparison of the different methods.

```bash
/gsc/software/linux-x86_64-centos6/R-3.3.2/bin/Rscript ../plots/comparison.R curves.stats figure_comparison.png
```

The next is a comparison shown as Precision-Recall curves

```bash
/gsc/software/linux-x86_64-centos6/R-3.3.2/bin/Rscript ../plots/PRcurves.R curves.all figure_PRcurve.png
```

The next is a set of histograms comparing the different methods

```bash
/gsc/software/linux-x86_64-centos6/R-3.3.2/bin/Rscript ../plots/scores_breakdown.R scores.testing.svd scores.testing.other combinedData.testing.classes figure_scores.png
```

The next is an analysis of the years after the split year

```bash
/gsc/software/linux-x86_64-centos6/R-3.3.2/bin/Rscript ../plots/yearByYear.R yearByYear.results figure_yearByYear.png
```

## Make Predictions for Alzheimer's and Parkinson's Disease

We'll output predictions for Alzheimer's and Parkinson's.

```bash
# Store the CUIDs for Alzheimer's and Parkinson's
echo "C0002395" >> cuids.alzheimers.txt
echo "C0030567" >> cuids.parkinsons.txt
echo "C0242422" >> cuids.parkinsons.txt

# Use the CUIDs to find the row numbers for each term
grep -nFf cuids.alzheimers.txt umlsWordlist.WithIDs.txt | cut -f 1 -d ':' | awk ' { print $0-1; } ' > ids.alzheimers.txt
grep -nFf cuids.parkinsons.txt umlsWordlist.WithIDs.txt | cut -f 1 -d ':' | awk ' { print $0-1; } ' > ids.parkinsons.txt

# Get all terms that are of type Pharmacologic Substance (T121) or Clinical Drug (T200)
grep -n -P "(T121)|(T200)" umlsWordlist.WithIDs.txt | cut -f 1 -d ':' | awk ' { print $0-1; } ' > ids.drugs.txt

# Filter for those terms that actually appear in the matrix (using the trainingAndValidation.ids file)
grep -xFf finalDataset/trainingAndValidation.ids ids.drugs.txt > ids.drugs.txt.filtered
mv ids.drugs.txt.filtered ids.drugs.txt

# Start calculating scores
python ../analysis/calcSVDScores.py --svdU svd.all.U --svdV svd.all.V --svdSV svd.all.SV --idsFileA ids.alzheimers.txt --idsFileB ids.drugs.txt --sv $optimalSV --threshold $optimalThreshold --outFile predictions.alzheimers.txt

python ../analysis/calcSVDScores.py --svdU svd.all.U --svdV svd.all.V --svdSV svd.all.SV --idsFileA ids.parkinsons.txt --idsFileB ids.drugs.txt --sv $optimalSV --threshold $optimalThreshold --outFile predictions.parkinsons.txt

# Then filter out for only novel discoveries
bash ../combine_data/filterCooccurrences.sh predictions.alzheimers.txt finalDataset/all.ids finalDataset/all.cooccurrences predictions.alzheimers.novel.txt

bash ../combine_data/filterCooccurrences.sh predictions.parkinsons.txt finalDataset/all.ids finalDataset/all.cooccurrences predictions.parkinsons.novel.txt

# Lastly get the actual terms out of the file for the predictions and sort them
cat predictions.alzheimers.novel.txt | awk -v f=umlsWordlist.WithIDs.txt ' BEGIN { x=0; while (getline < f) dict[x++] = $0; } { print $0"\t"dict[$2]; } ' | sort -k3,3gr > predictions.alzheimers.novel.withterms.txt
cat predictions.parkinsons.novel.txt | awk -v f=umlsWordlist.WithIDs.txt ' BEGIN { x=0; while (getline < f) dict[x++] = $0; } { print $0"\t"dict[$2]; } ' | sort -k3,3gr > predictions.parkinsons.novel.withterms.txt

# Clean up
rm predictions.alzheimers.txt predictions.alzheimers.novel.txt
rm predictions.parkinsons.txt predictions.parkinsons.novel.txt

```

## Data Stats

Lastly we'll collect a few statistics about our dataset for the publcation.

```bash
grep -F "<Abstract>" medlineAndPMC/medline/*  | wc -l > summary.abstractCount
cat medlineAndPMC/pmcSummary.txt | wc -l > summary.articleCount

cat umlsWordlist.Final.txt | wc -l > summary.fullWordlistCount
cat finalDataset/all.ids | wc -l > summary.observedWordlistCount

cat finalDataset/trainingAndValidation.cooccurrences | wc -l > summary.trainingCooccurenceCount
cat finalDataset/trainingAndValidation.ids | wc -l > summary.trainingTermsCount
cat finalDataset/testing.all.cooccurrences | wc -l > summary.testingCooccurenceCount
```
