cd catalog_gen &&
./go>/dev/stderr&&
./calibrate.sh ../beast/polaris-1s-gain38-4.bmp>/dev/stderr &&
./hip2cat.sh >/dev/stderr&&
./db2beast.sh >/dev/stderr&&
cd ../beast &&
./go >/dev/stderr&&
[ `python getstars.py | tee /dev/stderr | wc -l` -ge 1 ] &&
[ `python gen_test_astrometry.py | tee /dev/stderr | wc -l` -ge 1 ] &&
[ `python gen_test_px.py | tee /dev/stderr | wc -l` -ge 1 ] &&
echo "all tests passed!"

