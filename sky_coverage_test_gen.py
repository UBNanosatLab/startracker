import numpy
import math
import sys
maxstep=float(sys.argv[1])
step=maxstep/math.sqrt(2)
decstep=180/math.floor(180/step)
for dec in list(numpy.arange(-90+decstep/2,90,decstep)):
	rastep=360/math.floor(360/(step/math.cos(math.radians(dec))))
	for ra in list(numpy.arange(0,360,rastep)):
		x=math.cos(math.radians(ra))*math.cos(math.radians(dec))
		y=math.sin(math.radians(ra))*math.cos(math.radians(dec))
		z=math.sin(math.radians(dec))
		print x,y,z,ra,dec
