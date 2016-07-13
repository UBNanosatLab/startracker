#!/bin/bash
source calibration/calibration.txt
#assumes that DEG_Y <= DEG_X
python gendb_fov_cutoff.py $DEG_Y $ARC_ERR > tmp1.dat
cut -d "," -f 2,3,4 --complement < nearStars.dat > tmp2.dat
cat tmp1.dat tmp2.dat | sort -u -t "," -n -k1,1n -k 2,2n -k3,3n -k4,4n > unprocessed.dat
python gendb_transpose.py $ARC_ERR | sort -u -t "," -n -k1,1n -k 2,2n -k3,3n -k4,4n > starnd.dat
python gendb_brightness.py $NOISE_MAG < starnd.dat | sort -u -t "," -n -k1,1n -k 2,2n -k3,3n -k4,4n > constellationdb.dat
