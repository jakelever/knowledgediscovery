#!/bin/bash

echo "set -euxo pipefail" > README_abstracts.sh
cat README_abstracts.md | awk -F '' ' { if ($0=="```") code=0; if (code==1 || $1 == "#") print $0"\n"; if ($0=="```bash") code=1;}' >> README_abstracts.sh

bash README_abstracts.sh

