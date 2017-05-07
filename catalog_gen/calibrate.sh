#!/bin/bash

echo "POS_ERR_SIGMA=1.8" > calibration/calibration.txt
echo "IMAGE_MAX=255" >> calibration/calibration.txt
echo "PSF_RADIUS=3.5" >> calibration/calibration.txt
#Use MIN_MAG=None with real startracker
echo "MIN_MAG=4.6" >> calibration/calibration.txt
echo "MAX_FALSE_STARS=7" >> calibration/calibration.txt

#Set threshold so that there is a 50% chance of a star apearing above the threshold per image
echo "PROB_FALSE_STAR=0.5" >> calibration/calibration.txt

#50 percent of stars fall within 1 sigma. This should probably be at least 2
echo "MAG_BOUND_SIGMA=2" >> calibration/calibration.txt

#this also copies the image for use by astrometry
python image_stats.py >> calibration/calibration.txt
cd calibration
for i in ../../beast/bg_sample/*.png; do
	IMAGE_NAME="`basename $i`"
	solve-field --skip-solved --cpulimit 60 $IMAGE_NAME
	#solve-field --overwrite --cpulimit 60 $IMAGE_NAME
done
for i in *.solved; do
	wcsinfo `basename $i .solved`.wcs  | tr [:lower:] [:upper:] | tr " " "=" | grep "=[0-9.-]*$" > $i
	source $i
	echo "IMG_X=$IMAGEW" >>$i
	echo "IMG_Y=$IMAGEH" >>$i
	echo "DEG_X=$FIELDW" >>$i
	echo "DEG_Y=$FIELDH" >>$i
done

python ../star_corr.py *.solved>>calibration.txt
source calibration.txt
echo "ARC_ERR_REL=$ARC_ERR" >>calibration.txt
echo "POS_VARIANCE_REL=$POS_VARIANCE" >>calibration.txt
