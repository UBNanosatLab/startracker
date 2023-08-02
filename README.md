Note: the startracker code in this repository is depricated. Use https://github.com/UBNanosatLab/openstartracker instead

For starfield simulation, see the readme in the camera_simulator subdirectory. The code is embarasingly bad and requires gigabytes of GPU memory for absolutely no reason. It is in desperate need of a rewrite, however I am making it avalible due to public interest

## Basic setup:

##### From a fresh xubuntu 16.04 linux install
~~~~
sudo apt-get install git libvte-dev libtool ctags gdb meld nemiver libwebkit-dev vim geany geany-plugins astrometry.net python-astropy  g++-multilib
sudo apt-get install python-scipy libopencv-dev python-opencv swig
cd /usr/share/astrometry
sudo wget http://data.astrometry.net/4100/index-4112.fits
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

