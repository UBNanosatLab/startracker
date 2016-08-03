#!/bin/bash
awk  -F '|' '
BEGIN {
	deg2rad = atan2(0, -1)/180;
	yeardiff=strftime("%Y")+(strftime("%m")-1)/12-1991.25
}
($30==0||$30==1)&&$7!=3{
	HIP_ID=$2;
	MAG=$6;
	DEC=yeardiff*$14/3600000 + $10;
	cosdec=cos(deg2rad*DEC);
	RA=yeardiff*$13/(cosdec*3600000) + $9;
	X=cos(deg2rad*RA)*cosdec;
	Y=sin(deg2rad*RA)*cosdec;
	Z=sin(deg2rad*DEC);
	MAX_BRIGHTNESS=10^($50/-2.5);
	MIN_BRIGHTNESS=10^($51/-2.5);
	printf("%d %.12g %.12g %.12g %.12g %.12g %.12g %.12g %.12g\n",HIP_ID,MAG,RA,DEC,X,Y,Z,MAX_BRIGHTNESS,MIN_BRIGHTNESS)
}' hip_main.dat >catalog.dat
