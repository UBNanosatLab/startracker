import numpy as np
from scipy import spatial
import math
import sys
import heapq
import itertools, operator
import config

#this python file generates constelations based on what stars might be within a simulated field of view
#the purpose of this is to make the database robust against cases where part of a constelation is cut off, but we still have enough stars to form another constelation
#takes in 1 commandline argument. this is our minimum fov/2

execfile(config.PROJECT_ROOT+"catalog_gen/calibration/calibration.txt")
IMG_X=IMAGEW
IMG_Y=IMAGEH
DEG_X=FIELDW
DEG_Y=FIELDH


if ALLOW_BIG_CONSTELLATIONS==0:
	if DEG_X<DEG_Y:
		fovradius=DEG_X/2.0
	else:
		fovradius=DEG_Y/2.0
else:
	fovradius=math.sqrt(DEG_X*DEG_Y)/2

def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

#xyz_dist takes xyz of two points
#returns distance in degrees
def xyz_dist(xyz1,xyz2):
	return math.degrees(math.acos(np.clip(np.dot(xyz1,xyz2),a_min=-1,a_max=1)))
#star_dist takes ids of two stars,returns distance between them in arcseconds
def star_dist(s1,s2):
	return 3600*xyz_dist(stardb[s1][4:7],stardb[s2][4:7])

#load our star catalog, converting from id,ra,dec to x,y,z,id
def getstardb(filename=config.PROJECT_ROOT+"catalog_gen/catalog.dat"):
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
		UNRELIABLE=int(fields[9]);
		stardb[HIP_ID]=[HIP_ID,MAG,DEC,RA,X,Y,Z,MAX_BRIGHTNESS,MIN_BRIGHTNESS,UNRELIABLE]
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

#radius is in degrees
def searchxyz(starxyz,points,radius=fovradius):
	xyz = spatial.cKDTree(starxyz)
	pts = spatial.cKDTree(points)
	return pts.query_ball_tree(xyz,2*abs(math.sin(math.radians(radius)/2)))


#why IMAGE_STDEV*BRIGHT_ERR_SIGMA*2?
#since the brightness threshold of the image centroiding program is IMAGE_STDEV*BRIGHT_ERR_SIGMA
#we need to add an extra BRIGHT_ERR_SIGMA to make sure star brightnesses never drops below that amount
def filterbrightness():
	global stardb
	sd=np.array(stardb.values(),dtype = object)
	#estimate min mag from reference image
	minbright=IMAGE_STDEV*BRIGHT_ERR_SIGMA*2
	if(MIN_MAG!=None):
		for i in sd:
			if i[1]>minbright:
				del stardb[i[0]]
	else:	
		for i in sd:
			if i[8]<minbright:
				del stardb[i[0]]

def filterunreliable():
	global stardb
	sd=np.array(stardb.values(),dtype = object)
	for i in sd:
		if i[9]:
			del stardb[i[0]]

def filterdoublestars(r=PIXSCALE*2*PSF_RADIUS):
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
	sd=np.array(stardb.values(),dtype=object)
	err=ARC_ERR*2./3600.
	xyz=np.array(sd[:,4:7].tolist(),dtype=float)
	fovxyz=getglobe()
	result=searchxyz(xyz,fovxyz,fovradius)
	starlist=[]
	numgood=0
	for i in range(0,len(fovxyz)):
		if len(result[i])>3:
			numgood+=1
			dist=np.degrees(np.arccos(np.clip(np.sum(fovxyz[i]*xyz[result[i]],1),a_min=-1,a_max=1)))
			minidx=np.argmin(dist)
			dist=np.degrees(np.arccos(np.clip(np.sum(xyz[result[i][minidx]]*xyz[result[i]],1),a_min=-1,a_max=1)))
#			dist=np.degrees(np.arccos(np.clip(np.sum(xyz[i]*xyz[result[i]],1),a_min=-1,a_max=1)))
			maxsize=heapq.nsmallest(4,dist)[-1]+err
			starlist.append([int(sd[result[i][j]][0]) for j in range(0,len(dist)) if dist[j]<maxsize])
	print >>sys.stderr,"Database coverage: "+str(100.0*numgood/len(fovxyz)) + "% percent of the sky"
	return starlist

#this function takes in a sorted list, a key function and an error, and returns
#an iterator to every posible permutation of the list which is sorted to within +/- err
#example: sorted_perms(sorted([3,2,1],key=vp),vp,1):
#based on http://code.activestate.com/recipes/252178/

def star_permutations(stars,key_min=lambda x: x,key_max=lambda x: x):
	assert(len(stars)>3)
	def sp(sl):
		if len(sl) <=1:
			yield sl
		else:
			for perm in sp(sl[1:]):
				yield sl[0:1] + perm[:]
				for i in range(1,len(perm)+1):
					if key_min(perm[i-1])<=key_max(sl[0]):
						yield perm[:i] + sl[0:1] + perm[i:]
					else:
						break
	return [[i[0],i[1],i[2],i[3]] for i in sp(sorted(stars,key=key_min))]



def sort_uniq(sequence):
    return [i for i in itertools.imap(operator.itemgetter(0),itertools.groupby(sorted(sequence)))]

def transpose_distance(oldstars):
	global ARC_ERR
	global stardb
	err=ARC_ERR*2.
	newstars=[]
	for stars in oldstars:
		dist={}
		for i in stars:
			dist[i]=star_dist(stars[0],i)
		newstars+=star_permutations(stars,lambda s: dist[s],lambda s: dist[s]+err)
	return newstars

def transpose_brightness(oldstars):
	global stardb
	err=IMAGE_STDEV*BRIGHT_ERR_SIGMA+BRIGHTNESS_FUDGE
	newstars=[]
	clipmax=lambda s: s if s<IMAGE_MAX else IMAGE_MAX
	for stars in oldstars:
		newstars+=star_permutations(stars,lambda s: -clipmax(stardb[s][7]+err),lambda s: -clipmax(stardb[s][8]))
	return newstars

def print_constellations(starlist):
	for s in starlist:
		print star_dist(s[0],s[1]),star_dist(s[0],s[2]),star_dist(s[0],s[3]),star_dist(s[1],s[2]),star_dist(s[1],s[3]),star_dist(s[2],s[3]),s[0],s[1],s[2],s[3]

#only do this part if we were run as a python script
if __name__ == '__main__':
	filterunreliable()
	filterbrightness()
	filterdoublestars()
	starlist=sort_uniq(fovstars()+nearstars())
	#starlist=sort_uniq(fovstars())
	starlist=sort_uniq(transpose_distance(starlist))
	starlist=sort_uniq(transpose_brightness(starlist))
	print_constellations(starlist)
