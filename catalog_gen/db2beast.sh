#!/bin/bash
source calibration/calibration.txt
python gendb.py calibration/stars.txt calibration/constellations.txt calibration/dbsize.txt

source calibration/dbsize.txt
cat calibration/dbsize.txt

LUTSIZE=$[$PARAM*4]
PARAMSIZE=$[$NUMCONST*(8+4*6)]
STARTABLESIZE=$[$STARTABLE*4]
#4 integers to hold the star ids, and 1 pointer ofset from the base to the next location
echo -n "calulated size:  "
echo "$[($LUTSIZE+$PARAMSIZE+$STARTABLESIZE)] beastdb.bin"

./beastgen
echo -n "actual size:     "
wc -c beastdb.bin
#gzip -f beastdb.bin
#echo -n "conpressed size: "
#wc -c beastdb.bin.gz
