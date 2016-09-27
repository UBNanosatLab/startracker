#!/bin/bash


EXT="`echo \"$@\" | grep -o [^\.]*$`"
cp "$@" calibration/image.$EXT
cd calibration
solve-field --overwrite  image.$EXT | grep "[0-9]"
wcsinfo image.wcs  | tr [:lower:] [:upper:] | tr " " "=" | grep "=[0-9.]*$" > calibration.txt

echo "POS_ERR_SIGMA=1" >> calibration.txt
echo "POS_ERR_STDEV=.5" >> calibration.txt

echo "IMAGE_MAX=255" >> calibration.txt
echo "IMAGE_MEAN=1.7" >> calibration.txt
echo "IMAGE_STDEV=2.04" >>calibration.txt
echo "BRIGHT_ERR_SIGMA=5" >> calibration.txt

echo "REF_MAG=8.3" >> calibration.txt
echo "REF_VAL=31.0" >> calibration.txt

source calibration.txt

echo "ARC_PER_PIX=$PIXSCALE" >> calibration.txt
echo "ARC_ERR=`bc -l <<< $PIXSCALE*$POS_ERR_STDEV*$POS_ERR_SIGMA`" >> calibration.txt
echo "IMG_X=$IMAGEW" >> calibration.txt
echo "IMG_Y=$IMAGEH" >> calibration.txt
echo "DEG_X=$FIELDW" >> calibration.txt
echo "DEG_Y=$FIELDH" >> calibration.txt

