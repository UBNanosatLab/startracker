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
		star=line.split()
		stardb[int(star[0])]=star
	return stardb
	
stardb=getstardb()

def getstarxyz(sd):
	return np.array([[math.cos(math.radians(float(i[2])))*math.cos(math.radians(float(i[3]))),math.sin(math.radians(float(i[2])))*math.cos(math.radians(float(i[3]))),math.sin(math.radians(float(i[3])))] for i in sd])
	
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

def filtermagnitude(mag):
	global stardb
	sd=stardb.values()
	xyz=getstarxyz(sd)
	for i in sd:
		if float(i[1])>mag:
			del stardb[int(i[0])]

def filterdoublestars(r):
	global stardb
	sd=stardb.values()
	xyz=getstarxyz(sd)
	for i in searchxyz(xyz,xyz,r/3600.):
		for j in range(1,len(i)):
			k=int(sd[i[j]][0])
			if k in stardb:
				del stardb[k]
	
def nearstars():
	global fovradius
	global ARC_ERR
	global stardb
	sd=stardb.values()
	err=ARC_ERR*2./3600.
	xyz=getstarxyz(sd)
	result=searchxyz(xyz,xyz,fovradius)
	starlist=[]
	for i in range(0,len(xyz)):
		if len(result[i])>3:
			dist=[math.degrees(math.acos(j)) for j in np.clip(np.sum(xyz[i]*xyz[result[i]],1),a_min=-1,a_max=1)]
			maxsize=heapq.nsmallest(4,dist)[-1]+err
			starlist.append([int(sd[result[i][j]][0]) for j in range(0,len(dist)) if dist[j]<maxsize])
	return starlist

def fovstars():
	global fovradius
	global ARC_ERR
	global stardb
	sd=stardb.values()
	err=ARC_ERR*2./3600.
	xyz=getstarxyz(sd)
	fovxyz=getglobe()
	result=searchxyz(xyz,fovxyz,fovradius)
	starlist=[]
	for i in range(0,len(fovxyz)):
		if len(result[i])>3:
			dist=[math.degrees(math.acos(j)) for j in np.clip(np.sum(fovxyz[i]*xyz[result[i]],1),a_min=-1,a_max=1)]
			minidx=np.argmin(dist)
			dist=[math.degrees(math.acos(j)) for j in np.clip(np.sum(xyz[minidx]*xyz[result[i]],1),a_min=-1,a_max=1)]
			maxsize=heapq.nsmallest(4,dist)[-1]+err
			starlist.append([int(sd[result[i][j]][0]) for j in range(0,len(dist)) if dist[j]<maxsize])
	return starlist
			
#this function takes in a sorted list, a key function and an error, and returns 
#an iterator to every posible permutation of the list which is sorted to within +/- err
#example: sorted_perms(sorted([3,2,1],key=vp),vp,1):
def sorted_perms(sl,perm_key,err):
    if len(sl) <=1:
        yield sl
    else:
        for perm in sorted_perms(sl[1:],perm_key,err):
			yield sl[0:1] + perm[:]
			for i in range(1,len(perm)+1):
				if perm_key(perm[i-1])<=perm_key(sl[0])+err:
					yield perm[:i] + sl[0:1] + perm[i:]
				else:
					break

def sort_uniq(sequence):
    return itertools.imap(operator.itemgetter(0),itertools.groupby(sorted(sequence)))

#only do this part if we were run as a python script
if __name__ == '__main__':
	filtermagnitude(MIN_BRIGHT)
	filterdoublestars(ARC_PER_PIX*4)
	for i in sort_uniq(fovstars()+nearstars()):
		print [stardb[j][5] for j in i]
