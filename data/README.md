# Data Organisation

These are scripts for preparing input data (abstracts/articles) and the necessary wordlists.

## Pubmed & Pubmed Central

The key file is the (prepareMedlineAndPMCData.sh). This manages the other scripts for processing Pubmed & PMC files.

Basic usage is simple:

```bash
bash prepareMedlineAndPMCData.sh /home/me/directoryToStoreData
```

## UMLS wordlist

There is also a script to take the UMLS dataset and create a wordlist using the appropriate types of terms. You need to have already downloaded UMLS and you should have a directory where all the RRF files are found.

```bash
bash generateUMLSWordlist.sh /home/me/umls/META/ /home/me/directoryToStoreData/umls
```

