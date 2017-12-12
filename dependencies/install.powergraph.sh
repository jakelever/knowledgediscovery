#!/bin/bash
set -e -x

rm -fr PowerGraph

git clone https://github.com/jakelever/PowerGraph.git

cd PowerGraph

# Let's configure the project
./configure --no_mpi --no_jvm

# And then build the collaborative filtering library specifically
cd release/toolkits/collaborative_filtering/
make

