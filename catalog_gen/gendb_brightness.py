#!/usr/bin/python
import math
import itertools
import sys

brightness_err=float(sys.argv[1])

def valid_permutation(perm):
	global brightness_err
	for i in range(1,len(perm)):
		if (stardb[int(perm[i-1])][0]>(stardb[int(perm[i])][0]+brightness_err)):
			return 0
	return 1

stardb={}
starfile = open("nearStars.dat")
for line in starfile.readlines():
	star=line.rstrip(' \t').split(",")
	#ra=float(star[2])
	#dec=float(star[3])
	#x=math.cos(math.radians(ra))*math.cos(math.radians(dec))
	#y=math.sin(math.radians(ra))*math.cos(math.radians(dec))
	#z=math.sin(math.radians(dec))
	stardb[int(star[0])]=[float(star[1]),int(star[0])]

starfile = open("/dev/stdin")
for line in starfile.readlines():
	constelation=line.rstrip(' \t\r\n').split(",")
	if (len(constelation)>3):
		for i in itertools.permutations(constelation):
			if valid_permutation(i):
				print i[0]+","+i[1]+","+i[2]+","+i[3]
