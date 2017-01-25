cd catalog_gen &&
./go>/dev/stderr&&
./calibrate.sh ../beast/polaris-tenth-gain41-4.bmp>/dev/stderr &&
#./calibrate.sh ../beast/polaris-1s-gain38-4.bmp>/dev/stderr &&
#./calibrate.sh ../beast/webcam.png>/dev/stderr &&
./hip2cat.sh >/dev/stderr&&
./db2beast.sh >/dev/stderr&&
cd ../beast &&
#./go >/dev/stderr&&
echo -e "\nUsing ideal star locations:\n" &&
[ `python gen_test_px.py | tee /dev/stderr | wc -l` -ge 1 ] &&
echo -e "\nUsing astrometry centroiding:\n" &&
[ `python gen_test_astrometry.py | tee /dev/stderr | wc -l` -ge 1 ] &&
echo -e "\nUsing OpenCV centroiding:\n" &&
[ `python getstars.py | tee /dev/stderr | wc -l` -ge 1 ] &&
echo "all tests passed!"
