#!/bin/bash
source calibration/calibration.txt
./hip_to_catalog.sh $MIN_MAG
python remove_close_stars.py $ARC_PER_PIX
python gendb_nearstars.py $ARC_ERR
