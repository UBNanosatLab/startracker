#!/bin/bash
python gendb_fov_cutoff.py 2 > tmp1.dat
cut -d "," -f 2,3,4 --complement < nearStars.dat > tmp2.dat
cat tmp1.dat tmp2.dat | sort -u -t "," -n -k1,1n -k 2,2n -k3,3n -k4,4n > unprocessed.dat
python gendb_transpose.py | sort -u -t "," -n -k1,1n -k 2,2n -k3,3n -k4,4n > starnd.dat
python gendb_brightness.py 1 < starnd.dat | sort -u -t "," -n -k1,1n -k 2,2n -k3,3n -k4,4n > constellationdb.dat
