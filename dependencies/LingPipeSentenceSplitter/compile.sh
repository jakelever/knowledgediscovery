#!/bin/bash
set -x

# Get directory of script
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
lingpipeJar=$HERE/../lingpipe-4.1.2.jar

if [ ! -f $lingpipeJar ]; then
	echo "Expected Lingpipe JAR file at $lingpipeJar. Please download and put there"
	exit 1
fi

CLASSPATH=$lingpipeJar

version=1.6
javac -target $version -source $version -classpath $CLASSPATH LingpipeSentenceSplitter.java

