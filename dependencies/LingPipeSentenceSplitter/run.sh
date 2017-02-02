#!/bin/bash

lingpipeJar="lingpipe-4.1.0.jar"

# Check for Lingpipe in CLASSPATH
lingpipeSearchCount=`echo "$CLASSPATH" | tr ':' '\n' | xargs -I PATH basename PATH | grep -F -x $lingpipeJar | wc -l`
if [[ $lingpipeSearchCount -eq 0 ]]; then
	echo "Unable to find Lingpipe Jar: $lingpipeJar in CLASSPATH"
	exit 255
fi

HERE=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

java -classpath $CLASSPATH:$HERE LingpipeSentenceSplitter


