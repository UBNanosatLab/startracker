#!/bin/sh
source calibration/calibration.txt
python gendb_info.py < constellationdb.dat > info/starline.txt
NUMCONST="$[`wc -l info/starline.txt | grep -o '^[0-9]*'`]"
#2/5 was found experimentally to give the most evenly distributed database
MIDPOINT="$[$NUMCONST*2/5]"
PARAM1="`cut -d ',' -f 1 < info/starline.txt | sort -n | head -n $MIDPOINT | tail -n 1 | sed s:$:/$ARC_ERR:g|bc`"
PARAM2="`cut -d ',' -f 2 < info/starline.txt | sort -n | head -n $MIDPOINT | tail -n 1 | sed s:$:/$ARC_ERR:g|bc`"
PARAM3="`cut -d ',' -f 3 < info/starline.txt | sort -n | head -n $MIDPOINT | tail -n 1 | sed s:$:/$ARC_ERR:g|bc`"

echo PARAM1=$PARAM1>calibration/dbsize.txt
echo PARAM2=$PARAM2>>calibration/dbsize.txt
echo PARAM3=$PARAM3>>calibration/dbsize.txt
echo NUMCONST=$NUMCONST>>calibration/dbsize.txt
echo $PARAM1 $PARAM2 $PARAM3 $NUMCONST
echo $[($PARAM1*$PARAM2*$PARAM3*4/8+$NUMCONST*(8*6+4*5))/(1024*1024)] MB


