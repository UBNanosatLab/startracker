import numpy
import math
import sys

execfile("../catalog_gen/calibration/calibration.txt")
execfile("../catalog_gen/calibration/dbsize.txt")
#load our star catalog, converting from id,ra,dec to x,y,z,id
stardb={}
starfile = open("../catalog_gen/catalog.dat")
for line in starfile.readlines():
	star=line.rstrip(' \t').split(",")
	ra=float(star[2])
	dec=float(star[3])
	x=math.cos(math.radians(ra))*math.cos(math.radians(dec))
	y=math.sin(math.radians(ra))*math.cos(math.radians(dec))
	z=math.sin(math.radians(dec))
	stardb[int(star[0])]=[x,y,z,float(star[1]),int(star[0])]



#generate a list of coordinates which covers the sky completely
#with the constraint that the space between each point may be no more than fov/2
#the idea is we are simulating the process of pointing our camera at every possible region of sky

maxstep=DEG_Y/2.0
ra=0
dec=0

mindist=1000
starlist=[]
sl_idx=0
minidx=-1
fx=math.cos(math.radians(ra))*math.cos(math.radians(dec))
fy=math.sin(math.radians(ra))*math.cos(math.radians(dec))
fz=math.sin(math.radians(dec))
#iterate through the list of stars. 
for starid in stardb:
	xdot=stardb[starid][0]*fx
	ydot=stardb[starid][1]*fy
	zdot=stardb[starid][2]*fz
	dist=math.degrees(math.acos(xdot+ydot+zdot))
	#if it is within or field of view, add it to starlist
	if dist<maxstep:
		x=stardb[starid][0]
		y=stardb[starid][1]
		z=stardb[starid][2]
		px=(IMG_X/2)*(1+(y/x)/math.tan(DEG_X*math.pi/(180*2)))
		py=(IMG_Y/2)*(1-(z/x)/math.tan(DEG_Y*math.pi/(180*2)))
		print px,py,stardb[starid][3]

#print x,y,z,ra,dec
