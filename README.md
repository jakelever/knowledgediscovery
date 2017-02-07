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
bash ../data/generateUMLSWordlist.sh /projects/bioracle/ncbiData/umls/2016AB/META/ workingDir/
```

We then need to process this wordlist into a Python pickled file and remove stop-words and short words.

```bash
python ../text_extraction/cooccurrenceMajigger.py --termsWithSynonymsFile umlsWordlist.Final.txt --stopwordsFile ../data/selected_stopwords.txt --removeShortwords --binaryTermsFile_out umlsWordlist.Final.pickle
```

## Run text mining across all PubMed and PubMed Central

First we generate a list of commands to parse all the text files. This is for use on a cluster.

```bash
bash ../text_extraction/generateCommandLists.sh
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

## Run Singular Value Decomposition

## Generate negative data for comparison

## Calculate scores for positive & negative relationships

## Generate precision/recall curves for each method with associated statistics
