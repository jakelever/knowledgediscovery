#!/bin/bash
set -e -x

usage() {
	echo "Usage: `basename $0` UMLSDIR OUTDIR"
	echo ""
	echo "This is a master script that will prepare Medline/PMC files ready for processing"
	echo
	echo " medlinePMCDir - Directory in which to output files"
	echo ""
}
expectedArgs=1

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

# Points towards directory containing UMLS files
medlinePMCDir=$1
medlinePMCDir=`readlink -f $medlinePMCDir`

# Get directory where this script is
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# First we download all the files
bash $HERE/downloadMedlineAndPMC.sh $medlinePMCDir

# Then we create a summary of all the PMC articles
python $HERE/generatePMCSummary.py --pmcDir $medlinePMCDir/pmc --outFile $medlinePMCDir/pmcSummary.txt

# And we split out the PMIDs of the PMC articles (to avoid them when processing Medline)
cut -f 1 -d $'\t' $medlinePMCDir/pmcSummary.txt | sed -e '/^$/d' | sort -n -u > $medlinePMCDir/pmcPMIDs.txt

# Now we split the larger set of Medline XML files by publication date
mkdir $medlinePMCDir/filteredMedline
python $HERE/splitMedlineXMLDirByYear.py --medlineXMLDir $medlinePMCDir/medline --pmidExclusionFile $medlinePMCDir/pmcPMIDs.txt --outDir $medlinePMCDir/filteredMedline

mkdir $medlinePMCDir/unfilteredMedline
python $HERE/splitMedlineXMLDirByYear.py --medlineXMLDir $medlinePMCDir/medline --outDir $medlinePMCDir/unfilteredMedline

# And finally we generate lists of PMC articles based on publication date
bash $HERE/generateArticleListsByYear.sh $medlinePMCDir/pmcSummary.txt $medlinePMCDir/articleLists

