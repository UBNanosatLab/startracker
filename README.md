
###Basic setup:

#####From a fresh xubuntu 16.04 linux install
~~~~
sudo apt-get install git libvte-dev libtool ctags gdb meld nemiver libwebkit-dev vim geany geany-plugins astrometry.net python-astropy python-scipy libopencv-dev python-opencv g++-multilib swig
cd /usr/share/astrometry
sudo wget http://data.astrometry.net/4200/index-4212.fits
sudo wget http://data.astrometry.net/4100/index-4116.fits
sudo wget http://data.astrometry.net/4100/index-4117.fits
sudo wget http://data.astrometry.net/4100/index-4118.fits
sudo wget http://data.astrometry.net/4100/index-4119.fits
cd
git clone https://github.com/UBNanosatLab/startracker.git

cd startracker
python setup.py
~~~~
You must log out and then log back in for the changes in setup.py to take effect
~~~~

cd startracker
./startracker_unit_test.sh
~~~~

