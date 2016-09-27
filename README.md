
###Basic setup:

#####From a fresh xubuntu 16.04 linux install
~~~~
sudo apt-get install git libvte-dev libtool ctags gdb meld nemiver libwebkit-dev vim geany geany-plugins astrometry.net python-astropy python-scipy libopencv-dev python-opencv
cd /usr/share/astrometry
sudo wget http://data.astrometry.net/4200/index-4212.fits
cd
git clone https://github.com/UBNanosatLab/software-testing.git

cd software-testing/beast
./go
cd ../catalog_gen
./go
./calibrate.sh ../beast/polaris-1s-gain38-4.bmp
./hip2cat.sh
./db2beast.sh
~~~~
