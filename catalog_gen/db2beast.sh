#!/bin/bash
source calibration/calibration.txt
python gendb_info.py < constellationdb.dat > info/starline.txt
NUMCONST="$[`wc -l info/starline.txt | grep -o '^[0-9]*'`]"
#2/5 was found experimentally to give the most evenly distributed database
MIDPOINT="$[$NUMCONST*2/5]"
PARAM1="`cut -d ' ' -f 1 < info/starline.txt | sort -n | head -n $MIDPOINT | tail -n 1 | sed s:$:/$ARC_ERR:g|bc`"
PARAM2="`cut -d ' ' -f 2 < info/starline.txt | sort -n | head -n $MIDPOINT | tail -n 1 | sed s:$:/$ARC_ERR:g|bc`"
PARAM3="`cut -d ' ' -f 3 < info/starline.txt | sort -n | head -n $MIDPOINT | tail -n 1 | sed s:$:/$ARC_ERR:g|bc`"

echo PARAM1=$PARAM1>calibration/dbsize.txt
echo PARAM2=$PARAM2>>calibration/dbsize.txt
echo PARAM3=$PARAM3>>calibration/dbsize.txt
echo NUMCONST=$NUMCONST>>calibration/dbsize.txt
echo $PARAM1 $PARAM2 $PARAM3 $NUMCONST

#using a blocksize of 2 gives a factor of 8 improvement in space usage (each is an ofset from the base)
LUTSIZE=$[($PARAM1/2)*($PARAM2/2)*($PARAM3/2)*4]
#we have 6 parameters for verification, each stored as a double
PARAMSIZE=$[$NUMCONST*(8*6+4*5)]
#4 integers to hold the star ids, and 1 pointer ofset from the base to the next location
echo $[($LUTSIZE+$PARAMSIZE)/(1024*1024)] MB

#./beastgen $PARAM1 $PARAM2 $PARAM3 $NUMCONST $ARC_ERR <info/starline.txt
echo "./beastgen $PARAM1 $PARAM2 $PARAM3 $NUMCONST $ARC_ERR < info/starline.txt"
