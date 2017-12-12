#!/bin/bash
set -ex

rm -fr geniatagger-python-0.1 geniatagger-3.0.1

# First let's install GeniaTagger

wget http://www.nactem.ac.uk/tsujii/GENIA/tagger/geniatagger-3.0.1.tar.gz

tar xvf geniatagger-3.0.1.tar.gz

cd geniatagger-3.0.1

# Fix a missing header
echo "#include <cstdlib>" > morph2.cpp
cat morph.cpp >> morph2.cpp
mv morph2.cpp morph.cpp

make

cd -

rm geniatagger-3.0.1.tar.gz

# Then let's install a Python wrapper for it
wget https://pypi.python.org/packages/cf/19/f61aa1318ca440a834ce433c49832047919a9665c421a633fe32896455fb/geniatagger-python-0.1.tar.gz
tar xvf geniatagger-python-0.1.tar.gz
rm geniatagger-python-0.1.tar.gz
cd geniatagger-python-0.1
python setup.py install
cd ../
