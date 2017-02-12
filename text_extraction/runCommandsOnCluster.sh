#!/bin/bash
set -ex

commandList=$1
commandList=`readlink -f $commandList`

splitDir=commandSplit
rm -fr $splitDir
mkdir $splitDir
splitDir=`readlink -f $splitDir`

roughChunkCount=100
commandCount=`cat $commandList | wc -l`
lineCount=$((($commandCount/$roughChunkCount)+1))
split -d -l $lineCount -d -a 8 $commandList $splitDir/commands.

rm -fr bashLogs
mkdir bashLogs
cd bashLogs

memRequired=2G
clusterHeadNode=apollo
clusterSubCommand=qsub
#clusterFlags="-b y -V -q arc.q -P arc.prj -l mem_token=$memRequired,h_vmem=$memRequired,mem_free=$memRequired"
clusterFlags="-b y -V -q arc.q -P arc.prj -l mem_token=$memRequired,mem_free=$memRequired"
clusterStatCommand=qstat
noJobsString="Following jobs do not exist"

rm -f jobNumbers
for f in $splitDir/commands.*
do
	command="cd $PWD; $clusterSubCommand $clusterFlags bash $f"

	ssh $clusterHeadNode "$command" > retVal1 2>&1
	grep job retVal1 | grep -oP "[0-9]*" >> jobNumbers

#break
done

while true
do
	jobList=`cat jobNumbers | sort -un | tr '\n' ',' | sed -e 's/,$//'`
	command="$clusterStatCommand -j $jobList"

	# Check the status of jobs (and ignore failure)
	ssh $clusterHeadNode "$command" > retVal2 2>&1 | true
	
	if grep --silent "$noJobsString" retVal2; then
		echo "All jobs finished"
		break
	fi
done

completedCount=`grep -r -l "Finished" ../logs | wc -l`

if [[ $commandCount -eq $completedCount ]]; then
	echo "All good."
else
	echo "Something has failed"
	exit 255
fi

