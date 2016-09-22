#!/bin/bash
source calibration/calibration.txt
python gendb.py > calibration/constellations.txt
NUMCONST="$[`wc -l calibration/constellations.txt | grep -o '^[0-9]*'`]"
#2/5 was found experimentally to give the most evenly distributed database
MIDPOINT="$[$NUMCONST*2/5]"
PARAM1="`cut -d ' ' -f 1 < calibration/constellations.txt | sort -n | head -n $MIDPOINT | tail -n 1 | sed s:$:/$ARC_ERR:g|bc`"
PARAM2="`cut -d ' ' -f 2 < calibration/constellations.txt | sort -n | head -n $MIDPOINT | tail -n 1 | sed s:$:/$ARC_ERR:g|bc`"
PARAM3="`cut -d ' ' -f 3 < calibration/constellations.txt | sort -n | head -n $MIDPOINT | tail -n 1 | sed s:$:/$ARC_ERR:g|bc`"

echo PARAM1=$PARAM1>calibration/dbsize.txt
echo PARAM2=$PARAM2>>calibration/dbsize.txt
echo PARAM3=$PARAM3>>calibration/dbsize.txt
echo NUMCONST=$NUMCONST>>calibration/dbsize.txt

cat calibration/dbsize.txt
#using a blocksize of 2 gives a factor of 8 improvement in space usage (each is an offset from the base)
LUTSIZE=$[($PARAM1/2)*($PARAM2/2)*($PARAM3/2)*4]
#we have 6 parameters for verification, each stored as a double
#struct adds a random extra 4 bits because reasons :-(
PARAMSIZE=$[$NUMCONST*(8*6+4*5+4)]
#4 integers to hold the star ids, and 1 pointer ofset from the base to the next location
echo -n "calulated size:  "
echo "$[($LUTSIZE+$PARAMSIZE)] beastdb.bin"

#const. size should be 64 (why?)
./beastgen
echo -n "actual size:     "
wc -c beastdb.bin
#gzip -f beastdb.bin
#echo -n "conpressed size: "
#wc -c beastdb.bin.gz
