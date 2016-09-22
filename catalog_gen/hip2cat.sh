#!/bin/bash
source calibration/calibration.txt
awk -v REF_MAG="$REF_MAG" -v REF_VAL="$REF_VAL" -F '|' '
BEGIN {
	magconst=REF_MAG+2.5*log(REF_VAL)/log(10)
	deg2rad = atan2(0, -1)/180;
	yeardiff=strftime("%Y")+(strftime("%m")-1)/12-1991.25
}
{
	HIP_ID=$2;
	MAG=$6;
	DEC=yeardiff*$14/3600000 + $10;
	cosdec=cos(deg2rad*DEC);
	RA=yeardiff*$13/(cosdec*3600000) + $9;
	X=cos(deg2rad*RA)*cosdec;
	Y=sin(deg2rad*RA)*cosdec;
	Z=sin(deg2rad*DEC);
	MAX_BRIGHTNESS=10^(($50-magconst)/-2.5);
	MIN_BRIGHTNESS=10^(($51-magconst)/-2.5);
	UNRELIABLE=($30==0||$30==1)&&$7!=3?0:1;
	printf("%d %.12g %.12g %.12g %.12g %.12g %.12g %.12g %.12g %d\n",HIP_ID,MAG,RA,DEC,X,Y,Z,MAX_BRIGHTNESS,MIN_BRIGHTNESS,UNRELIABLE)
}' hip_main.dat >catalog.dat
