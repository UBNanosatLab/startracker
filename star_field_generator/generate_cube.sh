#!/bin/bash
hs=$[1024*$1]

python makemap.py $1
#convert starmap.png -fill white -pointsize 30  -gravity Center -annotate +0+0 'RA=180,DEC=0' -annotate +$hs+0 'RA=90,DEC=0' -annotate -$hs+0 'RA=270,DEC=0' -gravity West -annotate +0+0 'RA=0,DEC=0' -annotate +0+$[$hs*2/3] 'RA=0,DEC=-60' -annotate +0-$[$hs*2/3] 'RA=0,DEC=60'  starmap.png 
sphere2cube starmap.png -R 0 0 0 -t 28 -r $hs -f PNG
cp face_4_$hs.png ~/startracker/camera_simulator/Data_$hs/ft.png
cp face_1_$hs.png ~/startracker/camera_simulator/Data_$hs/rt.png
cp face_2_$hs.png ~/startracker/camera_simulator/Data_$hs/bk.png
cp face_3_$hs.png ~/startracker/camera_simulator/Data_$hs/lt.png
cp face_5_$hs.png ~/startracker/camera_simulator/Data_$hs/dn.png
cp face_6_$hs.png ~/startracker/camera_simulator/Data_$hs/up.png
scp face_4_$hs.png andrew@muri1.eng.buffalo.edu:~/startracker/camera_simulator/Data_$hs/ft.png
scp face_1_$hs.png andrew@muri1.eng.buffalo.edu:~/startracker/camera_simulator/Data_$hs/rt.png
scp face_2_$hs.png andrew@muri1.eng.buffalo.edu:~/startracker/camera_simulator/Data_$hs/bk.png
scp face_3_$hs.png andrew@muri1.eng.buffalo.edu:~/startracker/camera_simulator/Data_$hs/lt.png
scp face_5_$hs.png andrew@muri1.eng.buffalo.edu:~/startracker/camera_simulator/Data_$hs/dn.png
scp face_6_$hs.png andrew@muri1.eng.buffalo.edu:~/startracker/camera_simulator/Data_$hs/up.png
