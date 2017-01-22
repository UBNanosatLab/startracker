#!/bin/bash
hs=$[1024*$1]

if [[ ! -f face_1_$hs.png ]]; then 
	python makemap.py $1
	convert starmap.png -fill white -pointsize 30  -gravity Center -annotate +0+0 'RA=180,DEC=0' -annotate -$hs+0 'RA=90,DEC=0' -annotate +$hs+0 'RA=270,DEC=0' -gravity West -annotate +0+0 'RA=0,DEC=0' -annotate +0+$[$hs*2/3] 'RA=0,DEC=-60' -annotate +0-$[$hs*2/3] 'RA=0,DEC=60'  starmap.png 
	sphere2cube starmap.png -R 0 0 0 -t 28 -r $hs -f PNG
else
	cp face_4_$hs.png ../camera_simulator/Data_$hs/ft.png
	cp face_1_$hs.png ../camera_simulator/Data_$hs/rt.png
	cp face_2_$hs.png ../camera_simulator/Data_$hs/bk.png
	cp face_3_$hs.png ../camera_simulator/Data_$hs/lt.png
	cp face_6_$hs.png ../camera_simulator/Data_$hs/dn.png
	cp face_5_$hs.png ../camera_simulator/Data_$hs/up.png
	cd ../camera_simulator/
	rm Data
	ln -s Data_$hs Data
fi
