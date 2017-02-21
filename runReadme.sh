#!/bin/bash

echo "set -euxo pipefail" > README.sh
cat README.md | awk -F '' ' { if ($0=="```") code=0; if (code==1 || $1 == "#") print $0"\n"; if ($0=="```bash") code=1;}' >> README.sh

bash README.sh

