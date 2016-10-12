import numpy as np
import cv2
import time
from astropy import wcs
from astropy.io import fits
import beast
beast.load_db()

import os, sys
sys.path.append('../catalog_gen/')
os.chdir('../catalog_gen/')
from gendb import *

#use astrometry calibration data to correct for image distortion
#see http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html
wcslist = fits.open('calibration/image.wcs')
w = wcs.WCS(wcslist[0].header)
os.chdir("../beast")
def extract_stars(img):
    """
    Takes in a an image opencv image array

    Args:
        input_file: the image
    Returns:
        An array containing tuples of star info. Tuple format :(x,y,brightest value in star)

    """
    img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    img = cv2.GaussianBlur(img,(3,3),0)
    #removes areas of the image that don't meet our brightness threshold
    ret,thresh = cv2.threshold(img,IMAGE_MEAN+IMAGE_STDEV*BRIGHT_ERR_SIGMA,IMAGE_MAX,3)
    contours,heirachy = cv2.findContours(thresh,1,2);
    stars = []
    for c in contours:
        M = cv2.moments(c)
        if M['m00']>0:
            #this is how the x and y position are defined by cv2
            cx = M['m10']/M['m00']
            cy = M['m01']/M['m00']
            #the center pixel is used as the approximation of the brightest pixel
            #in the star in order to speed up the function by a factor of 10 and still
            #have beast return matches for constellations
            stars.append((cx,cy,cv2.getRectSubPix(img,(1,1),(cx,cy))))
            #stars.append((cx,cy,img[int(cy),int(cx)]))

    #use astrometry calibration data to correct for image distortion
    #see http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html
    results=np.array(stars)
    results[:,0:2]=w.sip_pix2foc(results[:,0:2],1)
    return results
class NoMatchesFound(Exception):
    pass

def rigid_transform_3D(A, B):
    """
    Takes in two matrices of points and finds the attitude matrix needed to
    transform one onto the other

    Input:
        A: nx3 matrix
        B: nx3 matrix
        Note: the "n" dimension of both matrices must match
    Output:
        attitude_matrix: returned as a numpy matrix
    """
    assert len(A) == len(B)

    # dot is matrix multiplication for array
    H =  np.dot(np.transpose(A),B)

    U, S, Vt = np.linalg.svd(H)

    attitude_matrix = np.dot(U,Vt)


    return attitude_matrix

def xyz_points(image_stars_info):
    star_points = []
    for pixel_x,pixel_y,mag in image_stars_info:
        #formula for converting from x,y, magnitude to x,y,z
        j=2*np.tan(DEG_X*np.pi/(180*2))*pixel_x/IMG_X #j=(x/z)
        k=2*np.tan(DEG_Y*np.pi/(180*2))*pixel_y/IMG_Y #k=y/z
        x=1./np.sqrt(j*j+k*k+1)
        y=j*x
        z=k*x
        star_points.append([x,y,z])
    return star_points

def group_stars(star_points ,false_stars = 12):
    if (len(star_points)<4):
        raise NoMatchesFound("Not enough stars")
    if (len(star_points)-4<false_stars):
        false_stars=len(star_points)-4
    star_kd = spatial.cKDTree(star_points)
    #arbitrarily chosen
    #second retval is the star array locations in tree.data
    results = star_kd.query(star_points,false_stars+4)
    return results[1]


def identify_stars(image_stars_info,star_points=[]):
    """
    Takes in a list with star tuples of the form (x,y,mag) and attempts to
    determing the attitude matrix that would transfrom the stars from the image
    to their locations in the database

    Input:
        image_stars_info: list of star tuples of the form (x,y,mag)
        star_points (optional): precomputed x,y,z values of image_stars_info
    Returns:
        matched_stars: database of stars that were matched in the form
	[im_id,db_id,[im_x,im_y,im_z],[db_x,db_y,db_z]]
    Raises:
        NoMatchesFound:
    """
    
    #give the option to pass in precomputed star points, but dont require it
    if (len(star_points)==0):
        star_points = xyz_points(image_stars_info)
    image_stars_info=np.array(image_stars_info)
    star_ids = []
    for group in group_stars(star_points):
         query = beast.star_query()
         for i in image_stars_info[group]:
             query.add_star(i[0],i[1],i[2])
         if (query.search_pilot()):
             star_ids.append([group[query.im_0],int(query.db_0)])
             star_ids.append([group[query.im_1],int(query.db_1)])
             star_ids.append([group[query.im_2],int(query.db_2)])
             star_ids.append([group[query.im_3],int(query.db_3)])
             break
    return [i+star_points[i[0]]+stardb[i[1]][4:7] for i in sort_uniq(star_ids)]

if __name__ == '__main__':
    filterunreliable()
    filterbrightness()
    filterdoublestars()
    img = cv2.imread("../catalog_gen/calibration/image.png")
    image_stars_info = extract_stars(img)
    star_points=xyz_points(image_stars_info)
    sq =identify_stars(image_stars_info,star_points)
    if (len(sq)>0):
        A=np.array([[i[2],i[3],i[4]] for i in sq])
        B=np.array([[i[5],i[6],i[7]] for i in sq])
        R=rigid_transform_3D(A,B)
        print A,B,R  
    #for i in extract_stars("polaris-1s-gain38-4.bmp"): print i[0],i[1],i[2]
