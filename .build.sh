#!/bin/bash
cd "${0%/*}"
OUTPUT="${1:-TA-tcpcheck.spl}"
pip install --upgrade --no-dependencies -t lib -r lib/requirements.txt
cd ..
tar -cpzf $OUTPUT --exclude=.* --exclude=package.json --overwrite TA-tcpcheck 