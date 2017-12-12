#!/bin/bash
set -e -x

usage() {
	echo "Usage: `basename $0` target"
	echo ""
	echo "This downloads the various Medline and PMC XML files"
	echo
	echo " target - Directory to store the Medline and PMC files"
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
target=$1
target=`readlink -f $target`

# Download MedLine
# Refer to https://www.nlm.nih.gov/databases/download/pubmed_medline.html
mkdir -p $target/medline
cd $target/medline
wget --no-verbose --no-parent --recursive --level=1 --no-directories ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/

# Download PMC
# Refer to http://www.ncbi.nlm.nih.gov/pmc/tools/ftp/
mkdir -p $target/pmc
cd $target/pmc
wget ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/comm_use.A-B.xml.tar.gz
wget ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/comm_use.C-H.xml.tar.gz
wget ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/comm_use.I-N.xml.tar.gz
wget ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/comm_use.O-Z.xml.tar.gz
wget ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/non_comm_use.A-B.xml.tar.gz
wget ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/non_comm_use.C-H.xml.tar.gz
wget ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/non_comm_use.I-N.xml.tar.gz
wget ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/non_comm_use.O-Z.xml.tar.gz

# Extract the Medline files
cd $target/medline
find $target/medline -name '*.xml.gz' |\
xargs -I FILE gunzip FILE

# Extract the PMC files
cd $target/pmc
find $target/pmc -name '*.tar.gz' |\
xargs -I FILE tar xvf FILE

# Some cleanup
rm -f $target/medline/*.md5
rm -f $target/pmc/*.tar.gz
