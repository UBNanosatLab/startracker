#!/bin/bash


EXT="`echo \"$@\" | grep -o [^\.]*$`"
cp "$@" calibration/image.$EXT
cd calibration
solve-field --overwrite  image.$EXT | grep "[0-9]" > image.txt
wcsinfo image.wcs  | tr [:lower:] [:upper:] | tr " " "=" | grep "=[0-9.]*$" > calibration.txt
source calibration.txt

echo "ARC_PER_PIX=$PIXSCALE" >> calibration.txt
echo "ARC_ERR=`bc -l <<< $PIXSCALE/2`" >> calibration.txt
echo "IMG_X=$IMAGEW" >> calibration.txt
echo "IMG_Y=$IMAGEH" >> calibration.txt
echo "DEG_X=$FIELDW" >> calibration.txt
echo "DEG_Y=$FIELDH" >> calibration.txt

echo "IMAGE_MAX=255" >> calibration.txt
echo "IMAGE_MEAN=1.7" >> calibration.txt
echo "BRIGHTNESS_SIGMA=7" >> calibration.txt

echo "REF_MAG=8.3" >> calibration.txt
echo "REF_VAL=31.0" >> calibration.txt
