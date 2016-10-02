
import os, sys

sys.path.append('../catalog_gen/')
os.chdir('../catalog_gen/')

from gendb import *
from astropy import wcs

filterunreliable()
filterbrightness()
filterdoublestars()

ra=93.2341656425
dec=86.2682656958

ra_center=116.321270769
dec_center=86.5582328937

x=math.cos(math.radians(ra))*math.cos(math.radians(dec))
y=math.sin(math.radians(ra))*math.cos(math.radians(dec))
z=math.sin(math.radians(dec))


x_center=math.cos(math.radians(ra_center))*math.cos(math.radians(dec_center))
y_center=math.sin(math.radians(ra_center))*math.cos(math.radians(dec_center))
z_center=math.sin(math.radians(dec_center))

fovradius=4.545 / 2
orientation=119.27164
#orientation=180


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

sd=np.array(stardb.values(),dtype = object)
xyz = spatial.cKDTree(np.array(sd[:,4:7].tolist(),dtype=float))

result=sd[xyz.query_ball_point([x_center,y_center,z_center],2*abs(math.sin(math.radians(fovradius)/2)))]

result[:,4:7] = np.transpose(np.dot(rotation_matrix([0, 0, 1], math.radians(-ra)), np.transpose(result[:,4:7])))
result[:,4:7] = np.transpose(np.dot(rotation_matrix([0, 1, 0], math.radians(dec)), np.transpose(result[:,4:7])))

#center_xyz=[x_center,y_center,z_center]
#center_xyz=np.dot(rotation_matrix([0, 0, 1], math.radians(-ra)), center_xyz)
#center_xyz=np.dot(rotation_matrix([0, 1, 0], math.radians(dec)), center_xyz)
#print center_xyz
result[:,4:7] = np.transpose(np.dot(rotation_matrix([1,0,0], math.radians(orientation)), np.transpose(result[:,4:7])))

result[:,5:6]=(result[:,5:6]/result[:,4:5])*(IMG_X/2)/np.tan(DEG_X*np.pi/(180*2))
result[:,6:7]=(result[:,6:7]/result[:,4:5])*(IMG_Y/2)/np.tan(DEG_Y*np.pi/(180*2))
for i in result:
	print i[5],i[6],i[7]
