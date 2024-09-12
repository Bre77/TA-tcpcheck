#!/bin/bash
cd "${0%/*}"
OUTPUT="${1:-TA-tcpcheck.spl}"
chmod -R u=rwX,go= *
chmod -R u-x+X *
chmod -R u=rwx,go= *
python3.9 -m pip install --upgrade -t lib -r lib/requirements.txt --no-dependencies
cd ..
tar -cpzf $OUTPUT --exclude=.* --exclude=package.json --overwrite TA-tcpcheck 