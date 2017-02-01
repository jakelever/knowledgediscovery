# Knowledge Discovery using Recommendation Systems

All this code WILL BE in a master script that can run the entire analysis.

## Download PubMed and PubMed Central

We need to download the abstracts from PubMed and full text articles from the PubMed Central Open Access subset. This is all managed by the prepareMedlineANDPMCData.sh script.

```bash
bash data/prepareMedlineAndPMCData.sh /projects/bioracle/ncbiData/2017/
```

## Install UMLS

This involves downloading UMLS from https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html and running MetamorphoSys. Install the Active dataset. Unfortunately this can't currently be done via the command line.

## Create the UMLS-based word-list

A script will pull out the necessary terms, their IDs, semantic types and synonyms from the UMLS RRF files.

```bash
bash data/generateUMLSWordlist.sh /projects/bioracle/ncbiData/umls/2016AB/META/ workingDir/
```

## Run text mining across all PubMed and PubMed Central

## Combine data into a dataset for analysis

## Generate ANNI Vectors

## Run Singular Value Decomposition

## Generate negative data for comparison

## Calculate scores for positive & negative relationships

## Generate precision/recall curves for each method with associated statistics
