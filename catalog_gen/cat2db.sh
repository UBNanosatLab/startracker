#!/bin/bash
source calibration/calibration.txt
#assumes that DEG_Y <= DEG_X
python -c "from gendb import *;filtermagnitude(MIN_MAG);filterdoublestars(ARC_PER_PIX*4);nearstars();fovstars()" | sort -u -t " " -n -k1,1n -k 2,2n -k3,3n -k4,4n > unprocessed.dat
echo "done"
python gendb_transpose.py $ARC_ERR | sort -u -t "," -n -k1,1n -k 2,2n -k3,3n -k4,4n > starnd.dat
python gendb_brightness.py $NOISE_BRIGHT < starnd.dat | sort -u -t "," -n -k1,1n -k 2,2n -k3,3n -k4,4n > constellationdb.dat
