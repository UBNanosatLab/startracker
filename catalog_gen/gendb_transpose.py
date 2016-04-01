#!/usr/bin/python
import math
import itertools
import sys

rad_err=math.radians(1.0/64.0)
first_star=-1
#return distance from first star
def dffs(curr_star):
	global first_star
	global stardb
	xdot=stardb[int(first_star)][0]*stardb[int(curr_star)][0]
	ydot=stardb[int(first_star)][1]*stardb[int(curr_star)][1]
	zdot=stardb[int(first_star)][2]*stardb[int(curr_star)][2]
	if xdot+ydot+zdot>1:
		return 0
	return math.acos(xdot+ydot+zdot)

def valid_permutation(perm):
	global rad_err
	for i in range(1,len(perm)):
		if (dffs(perm[i-1])>(dffs(perm[i])+rad_err)):
			return 0
	return 1

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

starfile = open("unprocessed.dat")
for line in starfile.readlines():
	constelation=line.rstrip(' \t\r\n').split(",")
	if (len(constelation)>3):
		first_star=constelation.pop(0)
		for i in itertools.permutations(constelation):
			if valid_permutation(i):
				print first_star+","+i[0]+","+i[1]+","+i[2]
