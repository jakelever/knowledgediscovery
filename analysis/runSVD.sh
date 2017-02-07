#!/bin/bash
set -e

# Set up defaults
mirror=NO
binarize=NO
logarithm=NO
mutualinformation=NO
fillDiagonal=NO

# Usage statement
usage() {
	echo "Usage: `basename $0` --dimension DIM --svNum SVNUM --matrix MATRIXFILE --outU OUTUFILE --outV OUTVFILE --outSV OUTSVFILE [--mirror] [--binarize] [--fillDiagonal] [--perfStats STATSFILE]"
	echo
	echo "This script runs an SVD decomposition of a square matrix using Graphlab Powergraph's implementation of SVD."
	echo
	echo "  -h/--help              : Display this help message"
	echo "  --dimension DIM        : The dimension of the square matrix file"
	echo "  --svNum SVNUM          : The desired number of singular values"
	echo "  --matrix MATRIXFILE    : The path of the matrix file"
	echo "  --outU OUTUFILE        : The path for the output U matrix file"
	echo "  --outV OUTVFILE        : The path for the output V matrix file"
	echo "  --outSV OUTSVFILE      : The path for the output singular values file"
	echo "  --mirror               : Optional parameter to mirror the data before creating the matrix (default=$mirror)"
	echo "  --binarize             : Optional parameter to binarize the matrix before performing SVD (default=$binarize)"
	echo "  --logarithm            : Optional parameter to log(+1) the matrix before performing SVD (default=$logarithm)"
	echo "  --mutualinformation            : Optional parameter to use mutual information of matrix before performing SVD (default=$mutualinformation)"
	echo "  --fillDiagonal         : Overwrite the diagonal with ones"
	echo "  --perfStats STATSFILE  : Optional file to store performance stats on Graphlab run"
	echo
}

while [[ $# > 0 ]]
do
	key="$1"

	case $key in
		-h|--help)
		usage
		exit 0
		;;
		--dimension)
		dimension="$2"
		shift # past argument
		;;
		--svNum)
		svNum="$2"
		shift # past argument
		;;
		--matrix)
		matrix="$2"
		shift # past argument
		;;
		--outU)
		outU="$2"
		shift # past argument
		;;
		--outV)
		outV="$2"
		shift # past argument
		;;
		--outSV)
		outSV="$2"
		shift # past argument
		;;
		--mirror)
		mirror=YES
		;;
		--binarize)
		binarize=YES
		;;
		--logarithm)
		logarithm=YES
		;;
		--mutualinformation)
		mutualinformation=YES
		;;
		--fillDiagonal)
		fillDiagonal=YES
		;;
		--perfStats)
		perfStats="$2"
		shift # past argument
		;;
		*)
		echo "Unknown parameters: $key"
		exit 255
		;;
	esac
	
	if [[ $# > 0 ]]; then
		shift # past argument or value
	fi
done

# Do some checking that all input is there and as expected (as much as possible)
integerRegex='^[0-9]+$'
if [ -z "$dimension" ]; then
	echo "ERROR: --dimension must be set" >&2; usage; exit 255
elif [ -z "$svNum" ]; then
	echo "ERROR: --svNum must be set" >&2; usage; exit 255
elif [ -z "$matrix" ]; then
	echo "ERROR: --matrix must be set" >&2; usage; exit 255
elif [ -z "$outU" ]; then
	echo "ERROR: --outU must be set" >&2; usage; exit 255
elif [ -z "$outV" ]; then
	echo "ERROR: --outV must be set" >&2; usage; exit 255
elif [ -z "$outSV" ]; then
	echo "ERROR: --outSV must be set" >&2; usage; exit 255
elif ! [[ "$dimension" =~ $integerRegex ]]; then
	echo "ERROR: --dimension should be an integer : $dimension" >&2; usage; exit 255
elif ! [[ "$svNum" =~ $integerRegex ]]; then
	echo "ERROR: --svNum should be an integer : $svNum" >&2; usage; exit 255
elif ! [ -r $matrix ]; then
	echo "ERROR: Matrix file cannot be accessed : $matrix" >&2; usage; exit 255
elif [[ "$binarize" == "YES" && "$logarithm" == "YES" ]]; then
	echo "ERROR: --binarize and --logarithm cannot be used together" >&2; usage; exit 255
fi

HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT=`readlink -f $HERE/../`
GRAPHLAB=$PROJECT_ROOT/dependencies/PowerGraph/release/toolkits/collaborative_filtering

# Check that the Graphlab app is executable
if ! [[ -x $GRAPHLAB/svd ]]; then
	echo "Cannot execute Graphlab svd"
	echo "Looking in $GRAPHLAB"
	exit 255
fi

# TODO: Check that the matrix file is in the expected format
# TODO: Check that the matrix file has coordinates inside the appropriate range

echo "------------------------"
echo " `basename $0`"
echo "------------------------"
echo "Parameters:"
echo " --dimension $dimension"
echo " --svNum $svNum"
echo " --matrix $matrix"
echo " --outU $outU"
echo " --outV $outV"
echo " --outSV $outSV"
echo " --mirror : $mirror"
echo " --binarize : $binarize"
echo " --logarithm : $logarithm"
echo " --mutualinformation : $mutualinformation"
echo " --fillDiagonal : $fillDiagonal"
echo " --perfStats $perfStats"
echo "------------------------"
echo

workingDir=$PWD/graphlab_tmp
mkdir -p $workingDir
rm -fr $workingDir/*

mkdir -p $workingDir/matrix

if [[ "$mirror" == "YES" ]]; then
	cat $matrix | awk ' { print $1"\t"$2"\t"$3; print $2"\t"$1"\t"$3; }' > $workingDir/tmpMatrix1
else
	ln -s `readlink -f $matrix` $workingDir/tmpMatrix1
fi

# Removing diagonals (and potentially put in a full "set" of diagonals)
if [[ "$fillDiagonal" == "YES" ]]; then
	cat $workingDir/tmpMatrix1 | awk -v dimension=$dimension ' { if ($1!=$2) print $1"\t"$2"\t"$3; } END { for(i=0;i<dimension;i++) print i"\t"i"\t1"; } ' > $workingDir/tmpMatrix2
else
	ln -s $workingDir/tmpMatrix1 $workingDir/tmpMatrix2
fi

# Binarizing or logarithm the matrix?
if [[ "$binarize" == "YES" ]]; then # Either binarize the matrix
	cat $workingDir/tmpMatrix2 | awk ' { print $1"\t"$2"\t1"; } ' > $workingDir/matrix/matrixFile
elif [[ "$logarithm" == "YES" ]]; then # Log the matrix
	cat $workingDir/tmpMatrix2 | awk ' { print $1"\t"$2"\t"log($3+1); } ' > $workingDir/matrix/matrixFile
elif [[ "$mutualinformation" == "YES" ]]; then # Log the matrix
	cat $workingDir/tmpMatrix2 | awk ' { count[$1] = count[$1] + $3; } END { for (id in count) print id"\t"count[id]; }  ' > $workingDir/linkCounts
	#cat $workingDir/tmpMatrix | awk -v f=$workingDir/linkCounts ' BEGIN { while (getline < f) { counts[$1] = $2; } }  { val=$3/(counts[$1]+counts[$2]-$3); print $1"\t"$2"\t"val; } ' > $workingDir/matrix/matrixFile
	cat $workingDir/tmpMatrix2 | awk -v f=$workingDir/linkCounts ' BEGIN { while (getline < f) { counts[$1] = $2; } }  { val=(1000000*$3)/(counts[$1]+counts[$2]-$3); printf "%d\t%d\t%f\n",$1,$2,val; } ' > $workingDir/matrix/matrixFile
else
	ln -s `readlink -f $workingDir/tmpMatrix2` $workingDir/matrix/matrixFile
fi
TARGET=$workingDir/matrix
LOG=$workingDir/log

NCPUS=`grep -c ^processor /proc/cpuinfo`  # number of cpus you want to use. let's try to detect how many
ROWS=$dimension # number of rows
COLS=$dimension # number of columns
NSV=$svNum # number of singular values you want
NV=$(($NSV+200))	# 200 more than $NSV (extra buffer needed for convergence accuracy)

MAXITER=10

OUT_DIR=$workingDir/out
mkdir -p $OUT_DIR
OUT=$OUT_DIR/out.$NSV

echo "Executing: $GRAPHLAB/svd $TARGET --ncpus=$NCPUS --rows=$ROWS --cols=$COLS --nsv=$NSV --nv=$NV --max_iter=$MAXITER --quiet=1 --save_vectors=1 --predictions=$OUT"
$GRAPHLAB/svd $TARGET --ncpus=$NCPUS --rows=$ROWS --cols=$COLS --nsv=$NSV --nv=$NV --max_iter=$MAXITER --quiet=1 --save_vectors=1 --predictions=$OUT &
graphlabPID=$!

# If needed, collect performance stats to file during this run
if ! [ -z $perfStats ]; then
	top -b -p $graphlabPID > $perfStats &
	perfPID=$!
	wait $graphlabPID
	graphlabExit=$?
	kill -9 $perfPID
	gzip --best $perfStats
else
	wait $graphlabPID
	graphlabExit=$?
fi

if [[ $graphlabExit -ne 0 ]]; then
        echo "svd FAILED."
        exit 255
fi

generatedSVNum=`grep -v -P ^% $OUT.singular_values | wc -l`
echo "SVD has generated $generatedSVNum singular values"

if [[ $generatedSVNum -lt $svNum ]]; then
	echo "ERROR: Number of generated singular values ($generatedSVNum) < desired number ($svNum)"
	echo "Exiting..."
	exit 255
fi

svNumPlusOne=$(($svNum+1))

echo "Copy output decomposition files..."
grep -v -P ^% $OUT.U.* | cut -f 1-$svNumPlusOne -d ' ' > $outU
grep -v -P ^% $OUT.V.* | cut -f 1-$svNumPlusOne -d ' ' > $outV
grep -v -P ^% $OUT.singular_values | head -n $svNum > $outSV

echo "Cleaning up temporary output files..."
rm -f $OUT.*

