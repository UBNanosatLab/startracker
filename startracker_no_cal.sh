cd catalog_gen &&
./go>/dev/stderr&&
./hip2cat.sh >/dev/stderr&&
#./calibrate.sh >/dev/stderr&&
./db2beast.sh >/dev/stderr&&
source calibration/calibration.txt&&
cd ../beast &&
./go >/dev/stderr&&
echo -e "\nUsing ideal star locations:\n" &&
[ `python gen_test_px.py 2>&1| tee /dev/stderr | wc -l` -ge 1 ] &&
echo -e "\nUsing astrometry centroiding:\n" &&
[ `python gen_test_astrometry.py 2>&1| tee /dev/stderr | wc -l` -ge 1 ] &&
echo -e "\nUsing OpenCV centroiding:\n" &&
[ `ls -1 bg_sample/*.png | python startracker.py 2>&1| tee /dev/stderr | wc -l` -ge 1 ]
#python ../arimatic9000.py && display /tmp/arimatic9000
