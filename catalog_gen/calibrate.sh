#!/bin/bash


convert "$@" calibration/image.png
cd calibration
solve-field --overwrite  image.png | grep "[0-9]"
wcsinfo image.wcs  | tr [:lower:] [:upper:] | tr " " "=" | grep "=[0-9.]*$" > calibration.txt


echo "IMAGE_MAX=255" >> calibration.txt
echo "BRIGHT_ERR_SIGMA=5" >> calibration.txt
python ../image_stats.py >> calibration.txt

source calibration.txt

echo "ARC_PER_PIX=$PIXSCALE" >> calibration.txt
echo "IMG_X=$IMAGEW" >> calibration.txt
echo "IMG_Y=$IMAGEH" >> calibration.txt
echo "DEG_X=$FIELDW" >> calibration.txt
echo "DEG_Y=$FIELDH" >> calibration.txt
echo "POS_ERR_SIGMA=6" >> calibration.txt
python ../star_corr.py >> calibration.txt
echo "ARC_ERR=`bc -l <<< $PIXSCALE*$POS_ERR_STDEV*$POS_ERR_SIGMA`" >> calibration.txt