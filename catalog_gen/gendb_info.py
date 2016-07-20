#!/usr/bin/python
import math
import sys

#re
def dot(s1_id,s2_id):
	global stardb
	xdot=stardb[int(s1_id)][0]*stardb[int(s2_id)][0]
	ydot=stardb[int(s1_id)][1]*stardb[int(s2_id)][1]
	zdot=stardb[int(s1_id)][2]*stardb[int(s2_id)][2]
	return xdot+ydot+zdot


stardb={}
starfile = open("nearStars.dat")
for line in starfile.readlines():
	star=line.rstrip(' \t').split(",")
	ra=float(star[2])
	dec=float(star[3])
	x=math.cos(math.radians(ra))*math.cos(math.radians(dec))
	y=math.sin(math.radians(ra))*math.cos(math.radians(dec))
	z=math.sin(math.radians(dec))
	stardb[int(star[0])]=[x,y,z,int(star[0])]

starfile = open("/dev/stdin")
for line in starfile.readlines():
	s=line.rstrip(' \t\r\n').split(",")
	newline=[]
	cos1=dot(s[0],s[1])
	cos2=dot(s[0],s[2])
	cos3=dot(s[0],s[3])
	cos4=dot(s[1],s[2])
	cos5=dot(s[1],s[3])
	cos6=dot(s[2],s[3])
	
	newline.append(str(3600*math.degrees(math.acos(cos1))))
	newline.append(str(3600*math.degrees(math.acos(cos2))))
	newline.append(str(3600*math.degrees(math.acos(cos3))))
	newline.append(str(3600*math.degrees(math.acos(cos4))))
	newline.append(str(3600*math.degrees(math.acos(cos5))))
	newline.append(str(3600*math.degrees(math.acos(cos6))))
	
	newline.append(s[0])
	newline.append(s[1])
	newline.append(s[2])
	newline.append(s[3])
		
	print " ".join(newline)
#print rad_err
