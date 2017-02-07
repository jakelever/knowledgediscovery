#!/bin/bash
set -e

usage() {
	echo "Usage: `basename $0` inPrefix outMatrix"
	echo ""
	echo "This script merges multiple files into a single file for use as a sparse matrix"
	echo "Files should contain one number per line"
	echo ""
	echo "  inPrefix - The directory with all files to be merged"
	echo "  outMatrix - Filename of output matrix file"
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

inPrefix=$1 # The prefix of input files
outMatrix=$2 # The output file path
mirror=0 # Whether to mirror the output matrix

# Get the directory of script for relative paths
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Starting parallel merge..."
# Run the parallel merge script and pass in a file-list using a search of $inDir
bash $HERE/helper_parallelMerge.sh <(find -L $inPrefix -type f) $outMatrix $HERE/helper_merge_0keys.sh $mirror
echo "Completed parallel merge."

