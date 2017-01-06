import numpy as np
import cv2
import time
from astropy import wcs
from astropy.io import fits
import beast
import datetime
beast.load_db()

import os, sys
from catalog_gen.gendb import *
from config import PROJECT_ROOT

#use astrometry calibration data to correct for image distortion
#see http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html
wcslist = fits.open(PROJECT_ROOT+'catalog_gen/calibration/image.wcs')
w = wcs.WCS(wcslist[0].header)
def extract_stars(img):
    """
    Takes in a an image opencv image array

    Args:
        input_file: the image
    Returns:
        An array containing tuples of star info. Tuple format :(x,y,brightest value in star)

    """
    img2 = img
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

    #use astrometry calibration data to correct for image distortion
    #see http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html
    for star in get_objects_of_interest(contours):
        extract_axes(img2,cv2.moments(star))

    #visualize(img2,contours)
    results=np.array(stars)
    results[:,0:2]=w.sip_pix2foc(results[:,0:2],1)
    return results
def get_objects_of_interest(contours):

    """
    Returns a list of objects in the image that fall outside of 3 standard
    deviations of the mean. The mean and standard deviation of the axis ratios
    are used to determine what is anomalous stars
        Input:
            contours: the cv2 contours list of the stars in the image
        Return:
            list of objects found to be farther than 3 standard deviations
            from the mean
    """
    ratios = []
    ratio_to_contour={}
    angles = []
    angle_to_contour={}
    for c in contours:
        m =cv2.moments(c)
        if m["m00"]<=0:
            continue
        eig_val,eig_vec = get_eigens(m)
        axis_length = [4*np.sqrt(x) for x in eig_val]
        sorted(axis_length)
        ratio = axis_length[0]/axis_length[1]
        ratio_to_contour[ratio] = c
        ratios.append(ratio)

        angle = get_angle(m)
        angle_to_contour[angle] = c
        angles.append(angle)

    #better accuracy with double precision
    ratio_stddev=np.std(ratios,dtype=np.float64)
    ratio_mean = np.mean(ratios)

    angle_stddev=np.std(ratios,dtype=np.float64)
    angle_mean = np.mean(angles)

    ratios_of_interest = [ ratio_to_contour[x] for x in ratios if x>=ratio_mean+3*ratio_stddev or x<=ratio_mean-3*ratio_stddev]
    angles_of_interest = [ angle_to_contour[x] for x in angles if x>=angle_mean+3*angle_stddev or x<=angle_mean-3*angle_stddev]

    return ratios_of_interest+angles_of_interest

class NoMatchesFound(Exception):
    pass
def get_angle(moments):
    """
    Determines the orientation of the image from its moments
        Inputs:
            moments: list of image moments
    """
    assert moments["m00"] > 0
    cy = moments['m01']/moments['m00']
    cx = moments['m10']/moments['m00']
    u20 = moments["m20"]/moments["m00"] - cx**2
    u02 = moments["m02"]/moments["m00"] - cy**2
    u11 = moments["m11"]/moments["m00"] - cx*cy

    #definition of orientation angle
    return 0.5*np.arctan2(2*u11,(u20-u02))

def extract_via_mxb(start,end,length,img):
    """
    Extracts pixels along a line specified by a start and end point. The extracted
    pixels will be written to the array specified by $blank
        Input:
            start: a tuple of the start point (x,y)
            end: a tuple of the end point (x,y)
            length: the length of the line
                Note: this could be calculated but it has been calculated
                      in previous steps
            img: the image as a cv array to extract the pixels from
        Return:
            list containing the length of the line followed by that many rgb values
    """

    rise = (end[1]-start[1])/length
    run = (end[0]-start[0])/length
    next_pt = [x for x in start]
    results = [int(length)]
    for i in range(int(length)):
        next_pt[0]+=run
        next_pt[1]+=rise
        rgb = cv2.getRectSubPix(img,(1,1),(next_pt[0],next_pt[1]))[0][0]
        results.append(rgb)
    return results
def get_eigens(moments):
    """
    Calculates the eigenvectors and eigenvalues of the image from the moments
        Input:
            moments: list of moments
        Output:
            eigen_values: list of eigenvalues of the image
            eigen_vectors: list of unit eigenvectors centered at the centroid
                           of the image
    """

    assert moments["m00"] > 0
    #definition of covariance matrix from image moments
    cy = moments['m01']/moments['m00']
    cx = moments['m10']/moments['m00']
    u20 = moments["m20"]/moments["m00"] - cx**2
    u02 = moments["m02"]/moments["m00"] - cy**2
    u11 = moments["m11"]/moments["m00"] - cx*cy
    covariance = np.matrix([[u20,u11],[u11,u20]])

    return np.linalg.eig(covariance)

def extract_axes(image,moments):
    """
    Extracts pixels along the major and minor axis of a contour described by
    its moments
        Input:
            moments: the dictionary of image moments for an object
            image: the image that contains the object that will have its axes
                   extracted
        Return:
            Array containing just enough info to reconstruct the axes of the star.
            The method used to recreate the axis as they were in the picture
            can be found inside this method and inside extract_via_mxb.
            Format of returned list:
                eig_val: list of eigen_values
                eig_vec: list of eigen_vectors
                axis#: list containing the length of line preceded by that many rgb values

    """
    eig_val,eig_vec = get_eigens(moments)

    eig_vec1 = np.matrix.tolist(eig_vec[0])[0]
    eig_vec2 = np.matrix.tolist(eig_vec[1])[0]

    # 4 = constant of proportionality
    axis_length = [4*np.sqrt(x) for x in eig_val]

    #draw lines on axes
    cy = moments['m01']/moments['m00']
    cx = moments['m10']/moments['m00']
    #start and enpoints of lines
    x11=(int(cx-eig_vec1[0]*axis_length[1]/2),int(cy-eig_vec1[1]*axis_length[1]/2))
    x12=(int(cx+eig_vec1[0]*axis_length[1]/2),int(cy+eig_vec1[1]*axis_length[1]/2))
    x21=(int(cx-eig_vec2[0]*axis_length[0]/2),int(cy-eig_vec2[1]*axis_length[0]/2))
    x22=(int(cx+eig_vec2[0]*axis_length[0]/2),int(cy+eig_vec2[1]*axis_length[0]/2))

    axis1 = extract_via_mxb(x11,x12,axis_length[1],image)
    axis2 = extract_via_mxb(x21,x22,axis_length[0],image)
    return [eig_val,eig_vec,axis1,axis2]

def visualize(image,contours):
    """
    Purely used to visualize the axis work. Draws the axes on the stars in
    bright lime green.
        Input:
            image: the image to have the axes drawn on its objects
            contours: list of contours in the object
    """
    for c in contours:
        moments = cv2.moments(c)
        if(moments["m00"]<=0):
            continue;
        eig_val,eig_vec = get_eigens(moments)

        eig_vec1 = np.matrix.tolist(eig_vec[0])[0]
        eig_vec2 = np.matrix.tolist(eig_vec[1])[0]

        # 4 = constant of proportionality
        axis_length = [4*np.sqrt(x) for x in eig_val]

        cy = moments['m01']/moments['m00']
        cx = moments['m10']/moments['m00']

        x11=(int(cx-eig_vec1[0]*axis_length[1]/2),int(cy-eig_vec1[1]*axis_length[1]/2))
        x12=(int(cx+eig_vec1[0]*axis_length[1]/2),int(cy+eig_vec1[1]*axis_length[1]/2))
        x21=(int(cx-eig_vec2[0]*axis_length[0]/2),int(cy-eig_vec2[1]*axis_length[0]/2))
        x22=(int(cx+eig_vec2[0]*axis_length[0]/2),int(cy+eig_vec2[1]*axis_length[0]/2))

        cv2.line(image,x11,x12,(0,255,0))
        cv2.line(image,x21,x22,(0,255,0))
    cv2.imshow("drawn",image)
    cv2.waitKey()

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
    """
    Converts the (x,y,magnitude) values to x,y,z points
        Input:
            image_stars_info: list of tuples in the form (x,y,magnitude)
        Output:
            star_points: a list of tuples in the form (x,y,z)
    """
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
    Takes in a list with star tuples of the form (x,y,mag) and attempts to                                                                                               orm (x,y,mag) and attempts to
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

def determine_rotation_matrix(img_path):
    """
    Takes in a pth to an image and determines the attitude of the satellite
    based on the contents of the starfield in the image_stars_info
    Input:
        img_path: absolute path to the image to be evalutated
    Returns:
        a 2D rotation matrix (numpy format) of the image passed in

    """
    filterunreliable()
    filterbrightness()
    filterdoublestars()
    img = None;
    if(img_path == NULL):
        img = cv2.imread(PROJECT_ROOT+"catalog_gen/calibration/image.png")
    else:
        img = cv2.imread(img_path)
    image_stars_info = extract_stars(img)
    star_points=xyz_points(image_stars_info)
    sq =identify_stars(image_stars_info,star_points)
    if (len(sq)>0):
        A=np.array([[i[2],i[3],i[4]] for i in sq])
        B=np.array([[i[5],i[6],i[7]] for i in sq])
        return rigid_transform_3D(A,B)


    #for i in extract_stars("polaris-1s-gain38-4.bmp"): print i[0],i[1],i[2]
if __name__ == '__main__':
    determine_rotation_matrix()
