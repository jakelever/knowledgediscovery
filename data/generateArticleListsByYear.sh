#!/bin/bash
set -x

maxArticlesPerFile=2000

usage() {
	echo "Usage: `basename $0` PMCSUMMARY OUTDIR"
	echo ""
	echo "This generates a lists of PubMedCentral files by publication year"
	echo "It will generate multiple files per publication year with a maximum of $maxArticlesPerFile per file."
	echo "The files are saved to the current directory"
	echo
	echo " PMCSUMMARY - The PMC Summary file for a set of PMC files"
	echo " OUTDIR - Directory in which to create files"
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

pmcSummary=$1
outDir=$2

# Create the outDir if it doesn't already exist
mkdir -p $outDir

# Strip off any final slash
outDir=`echo $outDir | sed -e 's|/$||'`

# Get the absolute path of the summary file
pmcSummary=`readlink -f $pmcSummary`

# Use the PMC summary file to generate files for each publication year containing the filenames of the PMC articles
cat $pmcSummary | grep -P MAIN$ | cut -f 4,5 -d $'\t' | awk -F $'\t' -v dir=$outDir ' { print $2 > dir"/"$1".unsplit" } '

# Then use split to split these file lists into sublists containing a max of ($maxArticlesPerFile) per file
find $outDir -type f | sort | grep -vF ".split." | sed -e 's/\.\///g' -e 's/\.unsplit//g' | xargs -I YEAR split -a 4 -d -l $maxArticlesPerFile YEAR.unsplit "YEAR.split."

# And then clean up by removing the unsplit files
find $outDir -type f -name '*.unsplit' | xargs rm


