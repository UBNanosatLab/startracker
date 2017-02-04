
from startracker import *

filterunreliable()
filterbrightness()
filterdoublestars()

if USE_WCS==1:
	ra=RA_TANGENT
	dec=DEC_TANGENT
	orientation=ORIENTATION
else:
	ra=RA_CENTER
	dec=DEC_CENTER
	orientation=ORIENTATION_CENTER

x=math.cos(math.radians(ra))*math.cos(math.radians(dec))
y=math.sin(math.radians(ra))*math.cos(math.radians(dec))
z=math.sin(math.radians(dec))



sd=np.array(stardb.values(),dtype = object)
xyz = spatial.cKDTree(np.array(sd[:,4:7].tolist(),dtype=float))

result=sd[xyz.query_ball_point([x,y,z],2*abs(math.sin(math.radians(fovradius)/2)))]
#convert from celestial frame to camera frame
result[:,4:7] = np.dot(result[:,4:7], rotation_matrix([0,0,1], math.radians(ra)))
result[:,4:7] = np.dot(result[:,4:7], rotation_matrix([0,1,0], math.radians(-dec)))
result[:,4:7] = np.dot(result[:,4:7], rotation_matrix([1,0,0], math.radians(-orientation)))

#convert x&y to image x and image y
result[:,5:6]=(result[:,5:6]/result[:,4:5])*(IMG_X/2)/np.tan(DEG_X*np.pi/(180*2))
result[:,6:7]=(result[:,6:7]/result[:,4:5])*(IMG_Y/2)/np.tan(DEG_Y*np.pi/(180*2))
if(MIN_MAG!=None):
	image_stars_info = [[i[5],i[6],i[7]] for i in result if i[1]<MIN_MAG]
else:
	image_stars_info = [[i[5],i[6],i[7]] for i in result]

sq=identify_stars(image_stars_info)
if (len(sq)>0):
    A=np.array([[i[2],i[3],i[4]] for i in sq])
    B=np.array([[i[5],i[6],i[7]] for i in sq])
    R=rigid_transform_3D(A,B)
    
