#!/bin/bash

echo "POS_ERR_SIGMA=2.5" > calibration/calibration.txt
echo "IMAGE_MAX=255" >> calibration/calibration.txt
echo "PSF_RADIUS=3.5" >> calibration/calibration.txt
#Use MIN_MAG=None with real startracker
echo "MIN_MAG=4.5" >> calibration/calibration.txt
echo "BRIGHTNESS_FUDGE=70" >> calibration/calibration.txt

#on a good camera, setting this to 1 may make things worse
echo "USE_WCS=0" >> calibration/calibration.txt

#calculate a noise threshold such that there is an average of
#NUM_FALSE_PIXELS pixels randomly above the threshold per image
echo "NUM_FALSE_PIXELS=3" >> calibration/calibration.txt

#if sky coverage is marginal, and fov is not square, set this to one
echo "ALL_THESE_SQUARES_MAKE_A_CIRCLE=0" >> calibration/calibration.txt

python image_stats.py "$@" >> calibration/calibration.txt
cd calibration
solve-field --overwrite  image.png
wcsinfo image.wcs  | tr [:lower:] [:upper:] | tr " " "=" | grep "=[0-9.-]*$" >> calibration.txt

cd ..
convert "$@" calibration/image.png
./hip2cat.sh >/dev/null
cd calibration


python ../star_corr.py >>calibration.txt
