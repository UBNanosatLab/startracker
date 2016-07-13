import numpy
import math
import sys

#this python file generates constelations based on what stars might be within a simulated field of view
#the purpose of this is to make the database robust against cases where part of a constelation is cut off, but we still have enough stars to form another constelation
#takes in 1 commandline argument. this is our minimum fov/2



rad_err=math.radians(float(sys.argv[2])*4./3600.)

center_star_x=0
center_star_y=0
center_star_z=0
def distance_min(sort_star):
	global center_star_x
	global center_star_y
	global center_star_z
	xdot=sort_star[0]*center_star_x
	ydot=sort_star[1]*center_star_y
	zdot=sort_star[2]*center_star_z
	if xdot+ydot+zdot>1:
		return 0
	return math.acos(xdot+ydot+zdot)

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
	stardb[int(star[0])]=[x,y,z,int(star[0])]



#generate a list of coordinates which covers the sky completely
#with the constraint that the space between each point may be no more than fov/2
#the idea is we are simulating the process of pointing our camera at every possible region of sky

maxstep=float(sys.argv[1])/2.0
step=maxstep/math.sqrt(2)
decstep=180/math.floor(180/step)
for dec in list(numpy.arange(-90+decstep/2,90,decstep)):
	rastep=360/math.floor(360/(step/math.cos(math.radians(dec))))
	for ra in list(numpy.arange(0,360,rastep)):
		mindist=1000
		starlist=[]
		sl_idx=0
		minidx=-1
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
				#find the star which is closest to the center
				if dist<mindist:
					mindist=dist
					minidx=sl_idx
					center_star_x=stardb[starid][0]
					center_star_y=stardb[starid][1]
					center_star_z=stardb[starid][2]
				sl_idx+=1
		if len(starlist)>3:
			#sort the list by how close it is to the center-most star in our fov, using the function distance_min
			starlist.sort(key=distance_min)#sort stars by dist to first star
			idlist=[]
			#get the distance between the fourth-center-most and the first-center-most star
			xdot=starlist[3][0]*center_star_x
			ydot=starlist[3][1]*center_star_y
			zdot=starlist[3][2]*center_star_z
			last_dist=math.acos(xdot+ydot+zdot)
			#output all stars which are within the error bounds
			#that might allow them to be considered closer than the fourth-center-most star
			for s in starlist:
				xdot=s[0]*center_star_x
				ydot=s[1]*center_star_y
				zdot=s[2]*center_star_z
				if xdot+ydot+zdot>1:
					curr_dist=0
				else:
					curr_dist=math.acos(xdot+ydot+zdot)
				if curr_dist<(last_dist+rad_err):
					idlist.append(str(s[3]))
			#print it out!
			print ",".join(idlist)
		#print x,y,z,ra,dec
