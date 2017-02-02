#!/bin/bash


convert "$@" calibration/image.png
cd calibration
#solve-field --overwrite  image.png | grep "[0-9]"
wcsinfo image.wcs  | tr [:lower:] [:upper:] | tr " " "=" | grep "=[0-9.-]*$" > calibration.txt

cd ..
./hip2cat.sh >/dev/null
cd calibration

echo "POS_ERR_SIGMA=2" >> calibration.txt
echo "IMAGE_MAX=255" >> calibration.txt
echo "PSF_RADIUS=3.5" >> calibration.txt
#Use MIN_MAG=None with real startracker
echo "MIN_MAG=None" >> calibration.txt
echo "BRIGHTNESS_FUDGE=10" >> calibration.txt
echo "NUM_FALSE_PIXELS=3" >> calibration.txt

#if sky coverage is marginal, set this to one
echo "ALLOW_BIG_CONSTELLATIONS=1" >> calibration.txt

python ../image_stats.py >> calibration.txt
python ../star_corr.py >>calibration.txt
