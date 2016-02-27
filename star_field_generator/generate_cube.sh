#!/bin/bash
hs=$[1024*$1]
python makemap.py $1
convert starmap.png -fill white -pointsize 30  -gravity Center -annotate +0+0 'RA=180,DEC=0' -annotate -$hs+0 'RA=90,DEC=0' -annotate +$hs+0 'RA=270,DEC=0' -gravity West -annotate +0+0 'RA=0,DEC=0' -annotate +0+$[$hs*2/3] 'RA=0,DEC=-60' -annotate +0-$[$hs*2/3] 'RA=0,DEC=60'  starmap.png 
sphere2cube starmap.png -R 0 0 0 -t 28 -r $hs -f PNG
#NConvert/nconvert -overwrite -out dds -o production/ft.dds face_4_$hs.png
#NConvert/nconvert -overwrite -out dds -o production/rt.dds face_1_$hs.png
#NConvert/nconvert -overwrite -out dds -o  production/bk.dds face_2_$hs.png
#NConvert/nconvert -overwrite -out dds -o  production/lt.dds face_3_$hs.png
#NConvert/nconvert -overwrite -out dds -o production/dn.dds face_5_$hs.png
#NConvert/nconvert -overwrite -out dds -o production/up.dds face_6_$hs.png

cp face_4_$hs.png production/ft.png
cp face_1_$hs.png production/rt.png
cp face_2_$hs.png production/bk.png
cp face_3_$hs.png production/lt.png
cp face_6_$hs.png production/dn.png
cp face_5_$hs.png production/up.png
