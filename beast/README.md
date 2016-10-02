#Building:


To compile beast, you need to do sudo apt-get install libopencv-dev

To compile python interface for beast.cpp:

g++ -O2 -fPIC -c beast_wrap.cxx -o beast_wrap.o -lstdc++ -I/usr/include/python2.7

g++ -shared -fPIC beast_wrap.o beast.o -so _beast.so

In python:
import beast

###Todo:
- Use astropy to make sense of astrometry xyls data
