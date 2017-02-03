#!/bin/bash

cat README.md | awk ' { if ($0=="```") code=0; if (code==1) print; if ($0=="```bash") code=1;}' > README.sh

sh README.sh

