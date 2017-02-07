#!/bin/bash
set -e

usage() {
	echo "Usage: cat FILES | bash `basename $0`"
	echo ""
	echo "This script merges data from STD IN containing single numbers"
	echo "The output (to STD OUT) will not be binarized."
	echo "NOTE: This script is used as a helper for the generate matrix & yearSplit scripts"
	echo ""
	echo "  cat FILES - Example command to pipe multiple files into script"
	echo ""
}
expectedArgs=0

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

# for example:
#
# input data:
# 8
# 4
# 9
# 1
#
# expected output (may be in different order)
# 17
# 4
# 1
awk '{ total=total+$1; } END { print total } '

