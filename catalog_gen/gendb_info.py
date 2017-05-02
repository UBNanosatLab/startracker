#!/usr/bin/python
import math
import sys
from numpy import clip

#re
def sdist3(s1_id,s2_id):
	global stardb
	x1=stardb[int(s1_id)][0]
	y1=stardb[int(s1_id)][1]
	z1=stardb[int(s1_id)][2]
	x2=stardb[int(s2_id)][0]
	y2=stardb[int(s2_id)][1]
	z2=stardb[int(s2_id)][2]
	a=x1*y2 - x2*y1
	b=x1*z2 - x2*z1
	c=y1*z2 - y2*z1
	return sqrt(a*a+b*b+c*c)


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
	sin1=sdist3(s[0],s[1])
	sin2=sdist3(s[0],s[2])
	sin3=sdist3(s[0],s[3])
	sin4=sdist3(s[1],s[2])
	sin5=sdist3(s[1],s[3])
	sin6=sdist3(s[2],s[3])
	
	newline.append(str(3600*math.degrees(math.asin(sin1))))
	newline.append(str(3600*math.degrees(math.asin(sin2))))
	newline.append(str(3600*math.degrees(math.asin(sin3))))
	newline.append(str(3600*math.degrees(math.asin(sin4))))
	newline.append(str(3600*math.degrees(math.asin(sin5))))
	newline.append(str(3600*math.degrees(math.asin(sin6))))
	
	newline.append(s[0])
	newline.append(s[1])
	newline.append(s[2])
	newline.append(s[3])
		
	print " ".join(newline)
#print rad_err
