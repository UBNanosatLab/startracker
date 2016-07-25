#!/usr/bin/python
import math
import itertools
import sys

I_minmag=pow(10,float(sys.argv[1])/-2.5)

def valid_permutation(perm):
	global I_minmag
	global stardb
	for i in range(1,len(perm)):
		#if star i-1 at its absolute brightest is brighter than star i at its least bright, we are good
		maxmag=-2.5*math.log10(I_minmag+pow(10,stardb[int(perm[i-1])][0]/-2.5))
		minmag=stardb[int(perm[i])][1]
		if (maxmag>minmag):
			return 0
	return 1

stardb={}
starfile = open("catalogRemoved.dat")
for line in starfile.readlines():
	star=line.rstrip(' \t').split(",")
	#[max,min,id]
	stardb[int(star[0])]=[float(star[4]),float(star[4]),int(star[0])]

starfile = open("/dev/stdin")
for line in starfile.readlines():
	constelation=line.rstrip(' \t\r\n').split(",")
	if (len(constelation)>3):
		for i in itertools.permutations(constelation):
			if valid_permutation(i):
				print i[0]+","+i[1]+","+i[2]+","+i[3]
