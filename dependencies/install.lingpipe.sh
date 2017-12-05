#!/bin/bash
set -ex

# Get directory of script
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ ! -f lingpipe-4.1.2.jar ]; then
	wget http://lingpipe-download.s3.amazonaws.com/lingpipe-4.1.2.jar
fi

# Simply go into the directory of the Java script and compile it to the class file
cd LingPipeSentenceSplitter
bash compile.sh

