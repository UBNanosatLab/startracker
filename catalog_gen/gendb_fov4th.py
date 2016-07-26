import numpy
import math
import sys

#this python file generates constelations based on what stars might be within a simulated field of view
#the purpose of this is to make the database robust against cases where part of a constelation is cut off, but we still have enough stars to form another constelation
#takes in 1 commandline argument. this is our minimum fov/2

execfile("calibration/calibration.txt")
execfile("calibration/dbsize.txt")

def minmag(sort_star):
	return sort_star[4]

#load our star catalog, converting from id,ra,dec to x,y,z,id
stardb={}
starfile = open("/dev/stdin")
for line in starfile.readlines():
	star=line.rstrip(' \t').split(",")
	ra=float(star[2])
	dec=float(star[3])
	x=math.cos(math.radians(ra))*math.cos(math.radians(dec))
	y=math.sin(math.radians(ra))*math.cos(math.radians(dec))
	z=math.sin(math.radians(dec))
	starid=int(star[0])
	stardb[starid]=[x,y,z,starid,float(star[1])]

#generate a list of coordinates which covers the sky completely
#with the constraint that the space between each point may be no more than fov/2
#the idea is we are simulating the process of pointing our camera at every possible region of sky

maxstep=DEG_Y/2.0
step=maxstep/math.sqrt(2)
decstep=180/math.floor(180/step)
for dec in list(numpy.arange(-90+decstep/2,90,decstep)):
	rastep=360/math.floor(360/(step/math.cos(math.radians(dec))))
	for ra in list(numpy.arange(0,360,rastep)):
		starlist=[]
		x=math.cos(math.radians(ra))*math.cos(math.radians(dec))
		y=math.sin(math.radians(ra))*math.cos(math.radians(dec))
		z=math.sin(math.radians(dec))
		#iterate through the list of stars. 
		for starid in stardb:
			#print stardb[starid]
			#print x,y,z
			xdot=stardb[starid][0]*x
			ydot=stardb[starid][1]*y
			zdot=stardb[starid][2]*z
			dist=math.degrees(math.acos(xdot+ydot+zdot))
			#if it is within or field of view, add it to starlist
			if dist<maxstep:
				starlist.append(stardb[starid])
		if len(starlist)>3:
			#sort the list by how close it is to the center-most star in our fov, using the function distance_min
			starlist.sort(key=minmag)#sort stars by dist to first star
			print x,y,z,ra,dec,starlist[3][3],starlist[3][4]
		else:
			print x,y,z,ra,dec,-1,9999
		#print x,y,z,ra,dec
