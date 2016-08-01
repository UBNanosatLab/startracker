#!/bin/bash
source calibration/calibration.txt
awk  -F '|' 'BEGIN {deg2rad = atan2(0, -1)/180;yeardiff=strftime("%Y")+(strftime("%m")-1)/12-1991.25} ($30==0||$30==1)&&$7!=3{DEC=yeardiff*$14/3600000 + $10; RA=yeardiff*$13/(cos(deg2rad*DEC)*3600000) + $9; printf("%d %.12g %.12g %.12g %.12g %.12g\n",$2,$6,RA,DEC,$50,$51)}' hip_main.dat >catalog.dat
#awk  -v MIN_MAG="$MIN_MAG" -F '|' 'BEGIN {deg2rad = atan2(0, -1)/180;yeardiff=strftime("%Y")+(strftime("%m")-1)/12-1991.25} ($30==0||$30==1)&&$7!=3&&$51<MIN_MAG{DEC=yeardiff*$14/3600000 + $10; RA=yeardiff*$13/(cos(deg2rad*DEC)*3600000) + $9; printf("%d,%.12g,%.12g,%.12g,%.12g,%.12g\n",$2,$6,RA,DEC,$50,$51)}' hip_main.dat|sort -t "," -n -k4,4n  -k1,1n >catalog.dat
