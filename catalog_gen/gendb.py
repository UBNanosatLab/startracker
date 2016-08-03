import numpy as np
from scipy import spatial
import math
import sys
import heapq
import itertools, operator

#this python file generates constelations based on what stars might be within a simulated field of view
#the purpose of this is to make the database robust against cases where part of a constelation is cut off, but we still have enough stars to form another constelation
#takes in 1 commandline argument. this is our minimum fov/2

execfile("calibration/calibration.txt")
execfile("calibration/dbsize.txt")

if DEG_X<DEG_Y:
	fovradius=DEG_X/2.0
else:
	fovradius=DEG_Y/2.0


#load our star catalog, converting from id,ra,dec to x,y,z,id
def getstardb(filename="catalog.dat"):
	stardb={}
	starfile = open(filename)
	for line in starfile.readlines():
		fields=line.split()
		HIP_ID=int(fields[0]);
		MAG=float(fields[1]);
		DEC=float(fields[2]);
		RA=float(fields[3]);
		X=float(fields[4]);
		Y=float(fields[5]);
		Z=float(fields[6]);
		MAX_BRIGHTNESS=float(fields[7]);
		MIN_BRIGHTNESS=float(fields[8]);
		stardb[HIP_ID]=[HIP_ID,MAG,DEC,RA,X,Y,Z,MAX_BRIGHTNESS,MIN_BRIGHTNESS]
	return stardb
	
stardb=getstardb()

#generate a list of coordinates which covers the sky completely
#with the constraint that the space between each point may be no more than fov/2
#the idea is we are simulating the process of pointing our camera at every possible region of sky
def getglobe():
	global fovradius
	globe=[]
	step=fovradius/math.sqrt(2)
	decstep=180/math.floor(180/step)
	for dec in list(np.arange(-90+decstep/2,90,decstep)):
		rastep=360/math.floor(360/(step/math.cos(math.radians(dec))))
		for ra in list(np.arange(0,360,rastep)):
			x=math.cos(math.radians(ra))*math.cos(math.radians(dec))
			y=math.sin(math.radians(ra))*math.cos(math.radians(dec))
			z=math.sin(math.radians(dec))
			globe.append([x,y,z])
	return np.array(globe)

def searchxyz(starxyz,points,radius=fovradius):
	xyz = spatial.cKDTree(starxyz)
	pts = spatial.cKDTree(points)
	return pts.query_ball_tree(xyz,2*abs(math.sin(math.radians(radius)/2)))

def filtermagnitude(minmag=MIN_MAG):
	global stardb
	sd=np.array(stardb.values(),dtype = object)
	for i in sd:
		if i[1]>minmag:
			del stardb[i[0]]

def filterdoublestars(r=ARC_PER_PIX*4):
	global stardb
	sd=np.array(stardb.values(),dtype = object)
	xyz=np.array(sd[:,4:7].tolist(),dtype=float)
	for i in searchxyz(xyz,xyz,r/3600.):
		for j in range(1,len(i)):
			k=sd[i[j]][0]
			if k in stardb:
				del stardb[k]
	
def nearstars():
	global fovradius
	global ARC_ERR
	global stardb
	sd=np.array(stardb.values(),dtype = object)
	err=ARC_ERR*2./3600.
	xyz=np.array(sd[:,4:7].tolist(),dtype=float)
	result=searchxyz(xyz,xyz,fovradius)
	starlist=[]
	for i in range(0,len(xyz)):
		if len(result[i])>3:
			dist=np.degrees(np.arccos(np.clip(np.sum(xyz[i]*xyz[result[i]],1),a_min=-1,a_max=1)))
			maxsize=heapq.nsmallest(4,dist)[-1]+err
			starlist.append([sd[result[i][j]][0] for j in range(0,len(dist)) if dist[j]<maxsize])
	return starlist

def fovstars():
	global fovradius
	global ARC_ERR
	global stardb
	sd=np.array(stardb.values(),dtype = object)
	err=ARC_ERR*2./3600.
	xyz=np.array(sd[:,4:7].tolist(),dtype=float)
	fovxyz=getglobe()
	result=searchxyz(xyz,fovxyz,fovradius)
	starlist=[]
	for i in range(0,len(fovxyz)):
		if len(result[i])>3:
			dist=np.degrees(np.arccos(np.clip(np.sum(fovxyz[i]*xyz[result[i]],1),a_min=-1,a_max=1)))
			minidx=np.argmin(dist)
			dist=np.degrees(np.arccos(np.clip(np.sum(xyz[i]*xyz[result[i]],1),a_min=-1,a_max=1)))
			maxsize=heapq.nsmallest(4,dist)[-1]+err
			starlist.append([int(sd[result[i][j]][0]) for j in range(0,len(dist)) if dist[j]<maxsize])
	return starlist
			
#this function takes in a sorted list, a key function and an error, and returns 
#an iterator to every posible permutation of the list which is sorted to within +/- err
#example: sorted_perms(sorted([3,2,1],key=vp),vp,1):

def star_permutations(stars,key_func=lambda x: x,err=0):
	assert(len(stars>3))
	def sp(sl):
		if len(sl) <=1:
			yield sl
		else:
			for perm in sp(sl[1:]):
				yield sl[0:1] + perm[:]
				for i in range(1,len(perm)+1):
					if key_func(perm[i-1])<=key_func(sl[0])+err:
						yield perm[:i] + sl[0:1] + perm[i:]
					else:
						break
	return [[i[0],i[1],i[2],i[3]] for i in sp(sorted(stars,key=key_func))]

def sort_uniq(sequence):
    return itertools.imap(operator.itemgetter(0),itertools.groupby(sorted(sequence)))


#only do this part if we were run as a python script
if __name__ == '__main__':
	filterdoublestars()
	filtermagnitude()
	for i in sort_uniq(fovstars()+nearstars()):
		print [stardb[j][5] for j in i]
