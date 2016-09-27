import os, sys
sys.path.append('../catalog_gen/')
os.chdir('../catalog_gen/')

from gendb import *

filterunreliable()
filterbrightness()
filterdoublestars()

ra=0
dec=0

#ra=116.321271
#dec=86.558233
#fovradius=2.9

x=math.cos(math.radians(ra))*math.cos(math.radians(dec))
y=math.sin(math.radians(ra))*math.cos(math.radians(dec))
z=math.sin(math.radians(dec))

sd=np.array(stardb.values(),dtype = object)
xyz = spatial.cKDTree(np.array(sd[:,4:7].tolist(),dtype=float))
result=sd[xyz.query_ball_point([x,y,z],2*abs(math.sin(math.radians(fovradius)/2)))]
result[:,5:6]=(IMG_X/2)*(1+(result[:,5:6]/result[:,4:5])/np.tan(DEG_X*np.pi/(180*2)))
result[:,6:7]=(IMG_Y/2)*(1-(result[:,6:7]/result[:,4:5])/np.tan(DEG_Y*np.pi/(180*2)))
for i in result:
	print i[5],i[6],i[7]
