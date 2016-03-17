import numpy
import math
import sys

#this python file generates constelations based on what stars might be within a simulated field of view
#the purpose of this is to make the database robust against cases where part of a constelation is cut off, but we still have enough stars to form another constelation
#takes in 1 commandline argument. this is our minimum fov/2



rad_err=math.radians(1.0/64.0)

min_x=0
min_y=0
min_z=0
def distance_min(item1):
	global min_x
	global min_y
	global min_z
	xdot=item1[0]*min_x
	ydot=item1[1]*min_y
	zdot=item1[2]*min_z
	if xdot+ydot+zdot>1:
		return 0
	return math.acos(xdot+ydot+zdot)


stardb={}
starfile = open("catalog.dat")
for line in starfile.readlines():
	star=line.rstrip(' \t').split(",")
	ra=float(star[2])
	dec=float(star[3])
	x=math.cos(math.radians(ra))*math.cos(math.radians(dec))
	y=math.sin(math.radians(ra))*math.cos(math.radians(dec))
	z=math.sin(math.radians(dec))
	stardb[int(star[0])]=[x,y,z,int(star[0])]


maxstep=float(sys.argv[1])
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
		for starid in stardb:
			#print stardb[starid]
			#print x,y,z
			xdot=stardb[starid][0]*x
			ydot=stardb[starid][1]*y
			zdot=stardb[starid][2]*z
			dist=math.degrees(math.acos(xdot+ydot+zdot))
			if dist<maxstep:
				starlist.append(stardb[starid])
				if dist<mindist:
					mindist=dist
					minidx=sl_idx
					min_x=stardb[starid][0]
					min_y=stardb[starid][1]
					min_z=stardb[starid][2]
				sl_idx+=1
		if len(starlist)>3:
			starlist.sort(key=distance_min)#sort stars by dist to first star
			idlist=[]
			xdot=starlist[3][0]*min_x
			ydot=starlist[3][1]*min_y
			zdot=starlist[3][2]*min_z
			last_dist=math.acos(xdot+ydot+zdot)
			for s in starlist:
				xdot=s[0]*min_x
				ydot=s[1]*min_y
				zdot=s[2]*min_z
				if xdot+ydot+zdot>1:
					curr_dist=0
				else:
					curr_dist=math.acos(xdot+ydot+zdot)
				if curr_dist<(last_dist+rad_err):
					idlist.append(str(s[3]))
			print ",".join(idlist)
		#print x,y,z,ra,dec
