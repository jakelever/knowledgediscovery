#!/bin/bash
set -x

lingpipeJar="lingpipe-4.1.0.jar"

# Check for Lingpipe in CLASSPATH
lingpipeSearchCount=`echo "$CLASSPATH" | tr ':' '\n' | xargs -I PATH basename PATH | grep -F -x $lingpipeJar | wc -l`
if [[ $lingpipeSearchCount -eq 0 ]]; then
	echo "Unable to find Lingpipe Jar: $lingpipeJar in CLASSPATH"
	exit 255
fi

javac -classpath $CLASSPATH LingpipeSentenceSplitter.java

