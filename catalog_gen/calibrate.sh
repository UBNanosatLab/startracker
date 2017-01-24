#!/bin/bash


convert "$@" calibration/image.png
cd calibration
solve-field --overwrite  image.png | grep "[0-9]"
wcsinfo image.wcs  | tr [:lower:] [:upper:] | tr " " "=" | grep "=[0-9.]*$" > calibration.txt

cd ..
./hip2cat.sh >/dev/null
cd calibration

echo "POS_ERR_SIGMA=2.5" >> calibration.txt
python ../../pos_err.py >>calibration.txt

echo "IMAGE_MAX=255" >> calibration.txt
echo "PSF_RADIUS=3.5" >> calibration.txt
python ../image_stats.py >> calibration.txt

source calibration.txt

echo "ARC_PER_PIX=$PIXSCALE" >> calibration.txt
echo "ARC_ERR=`bc -l <<< $PIXSCALE*$POS_ERR_STDEV*$POS_ERR_SIGMA`" >> calibration.txt
echo "IMG_X=$IMAGEW" >> calibration.txt
echo "IMG_Y=$IMAGEH" >> calibration.txt
echo "DEG_X=$FIELDW" >> calibration.txt
echo "DEG_Y=$FIELDH" >> calibration.txt
python ../star_corr.py >>calibration.txt
