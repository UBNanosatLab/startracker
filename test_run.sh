#!/bin/bash
cd beast
./go
cd ../catalog_gen
./go
./calibrate.sh ../beast/polaris-1s-gain38-4.bmp
echo "Filling star catalog with Hipparcos data..."
./hip2cat.sh
echo "Generating beast database..."
./db2beast.sh
cd ../beast
echo "Running beast2.py... "
python beast2.py
