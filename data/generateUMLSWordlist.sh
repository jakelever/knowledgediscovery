#!/bin/bash
set -e

# Get the location of this script for future use
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

usage() {
	echo "Usage: `basename $0` UMLSDIR OUTDIR"
	echo ""
	echo "This generates a word-list and associated UMLS CUID list"
	echo "It specifically focuses on semantic types in the following categories:"
	echo "               ANAT/CHEM/DISO/GENE/PHYS"
	echo "It specifically removes the Finding group (T033)."
	echo
	echo " UMLSDIR - Directory containing the various UMLS files"
	echo " OUTDIR - Directory in which to output files"
	echo ""
}
expectedArgs=2

# Show help message if desired
if [[ $1 == "-h" || $1 == '--help' ]]; then
	usage
	exit 0
# Check for expected number of arguments
elif [[ $# -ne $expectedArgs ]]; then
	echo "ERROR: Expecting $expectedArgs arguments"
	usage
	exit 255
fi

set -x

# Points towards directory containing UMLS files
umlsDir=$1
outDir=$2

# Get the absolute paths to directories
umlsDir=`readlink -f $umlsDir`
outDir=`readlink -f $outDir`

if ! [[ -r $umlsDir/MRCONSO.RRF ]]; then
	echo "Unable to access MRCONSO.RRF file. Are you sure it is in: $umlsDir ?" 1>&2; exit 255
elif ! [[ -r $umlsDir/MRSTY.RRF ]]; then
	echo "Unable to access MRSTY.RRF file. Are you sure it is in: $umlsDir ?" 1>&2; exit 255
fi

# Create the output directory if needed and move into it
mkdir -p $outDir
cd $outDir

# Do some cleanup just in case
rm -f SemGroups.txt SemGroups.filtered.txt SemGroups.filtered.ids.txt

# Download the semantic groups file
wget https://semanticnetwork.nlm.nih.gov/download/SemGroups.txt

# Extract groups associated with anatomy, chemicals, disorders, genes and phys
grep -P "^ANAT" SemGroups.txt > SemGroups.filtered.txt
grep -P "^CHEM" SemGroups.txt >> SemGroups.filtered.txt
grep -P "^DISO" SemGroups.txt >> SemGroups.filtered.txt
grep -P "^GENE" SemGroups.txt >> SemGroups.filtered.txt
grep -P "^PHYS" SemGroups.txt >> SemGroups.filtered.txt

# Remove the Finding group (T033)
grep -v Finding SemGroups.filtered.txt >> SemGroups.filtered.txt2
mv SemGroups.filtered.txt2 SemGroups.filtered.txt

# Get the type IDs for the groups described above
cut -f 3 -d '|' SemGroups.filtered.txt | sort -u > SemGroups.filtered.ids.txt

#$umlsDir/MRSTY.RRF
#$umlsDir/MRCONSO.RRF

semanticTypeIDs=`cat SemGroups.filtered.ids.txt | tr '\n' ',' | sed -e 's/,$//'`

python=/gsc/software/linux-x86_64/python-2.7.2/bin/python

$python $HERE/helper_generateUMLSWordlist.py --selectedTypeIDs $semanticTypeIDs --umlsConceptFile $umlsDir/MRCONSO.RRF --umlsSemanticTypesFile $umlsDir/MRSTY.RRF --outWordlistFile $outDir/umlsWordlist.WithIDs.txt

# To avoid confusion, let's clean up a bit
rm -f SemGroups.txt SemGroups.filtered.txt SemGroups.filtered.ids.txt

# Sort the umlsWordlist (which will be by the CUIDs in the first column)
sort $outDir/umlsWordlist.WithIDs.txt > $outDir/umlsWordlist.WithIDs.tmp
mv $outDir/umlsWordlist.WithIDs.tmp $outDir/umlsWordlist.WithIDs.txt

# And let's make the raw final word-list by removing CUIDs and SemanticTypeIDs
cut -f 3 -d $'\t' $outDir/umlsWordlist.WithIDs.txt > $outDir/umlsWordlist.Final.txt
