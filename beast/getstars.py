import numpy as np
import cv2
import time

#use astrometry calibration data to correct for image distortion
#see http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html


import os, sys
from catalog_gen.gendb import *
from config import PROJECT_ROOT

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

def body2ECI_RA_DEC_ORI(body2ECI):
	DEC=np.degrees(np.arcsin(body2ECI[0,2]))
	RA=np.degrees(np.arctan2(body2ECI[0,1],body2ECI[0,0]))
	ORIENTATION=np.degrees(-np.arctan2(body2ECI[1,2],body2ECI[2,2]))\
	#rotation about the y axis (-90 to +90)
	print >>sys.stderr, "DEC="+str(DEC)
	#rotation about the z axis (-180 to +180)
	print >>sys.stderr, "RA="+str(RA)
	#rotation about the camera axis (-180 to +180)
	print >>sys.stderr, "ORIENTATION="+str(ORIENTATION)
    
def rigid_transform_3D(A, B, weight=[]):
    """
    Takes in two matrices of points and finds the attitude matrix needed to
    transform one onto the other

    Input:
        A: nx3 matrix - x,y,z in body frame
        B: nx3 matrix - x,y,z in eci
        Note: the "n" dimension of both matrices must match
    Output:
        attitude_matrix: returned as a numpy matrix
    """
    assert len(A) == len(B)
    if (len(weight) == 0):
        weight=np.array([1]*len(A))
    # dot is matrix multiplication for array
    H =  np.dot(np.transpose(A)*weight,B)


    #calculate attitude matrix
    #from http://malcolmdshuster.com/FC_MarkleyMortari_Girdwood_1999_AAS.pdf
    U, S, Vt = np.linalg.svd(H)
    flip=np.linalg.det(U)*np.linalg.det(Vt)

    #why was this not in here before?!
    U[:,2]*=flip

    body2ECI = np.dot(U,Vt)
    body2ECI_RA_DEC_ORI(body2ECI)
    return body2ECI

median_image=cv2.imread(PROJECT_ROOT+"beast/median_image.png")
def extract_stars(img,configfile=None,outputimg=0):
    """
    Takes in a an image opencv image array

    Args:
        input_file: the image
    Returns:
        An array containing tuples of star info. Tuple format :(x,y,brightest value in star)

    """
    
    #this is used in star_corr.py when we have multipule sets of calibration data to choose from
    global IMG_X
    global IMG_Y
    global DEG_X
    global DEG_Y
    if (configfile != None):
		tmp={}
		execfile(configfile,tmp)
		IMG_X=tmp['IMG_X']
		IMG_Y=tmp['IMG_Y']
		DEG_X=tmp['DEG_X']
		DEG_Y=tmp['DEG_Y']
    #execfile('/home/andrew/startracker/catalog_gen/calibration/w1.solved')
    #subtract average background from image
    img=img.astype(np.int16)-median_image.astype(np.int16)
    img=img.clip(0)
    img=img.astype(np.uint8)
    img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    img = cv2.GaussianBlur(img,(3,3),0)
    #removes areas of the image that don't meet our brightness threshold
    ret,thresh = cv2.threshold(img,BRIGHT_THRESH,IMAGE_MAX,cv2.THRESH_BINARY)
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
    results=np.array(stars)
    results[:,0]=results[:,0]-IMG_X/2
    results[:,1]=results[:,1]-IMG_Y/2
    if (outputimg==1):
        return (results,visualize(img,contours))
    else:
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
    image = cv2.cvtColor(image,cv2.COLOR_GRAY2RGB)
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
        try:
		    x11=(int(cx-eig_vec1[0]*axis_length[1]/2),int(cy-eig_vec1[1]*axis_length[1]/2))
		    x12=(int(cx+eig_vec1[0]*axis_length[1]/2),int(cy+eig_vec1[1]*axis_length[1]/2))
		    x21=(int(cx-eig_vec2[0]*axis_length[0]/2),int(cy-eig_vec2[1]*axis_length[0]/2))
		    x22=(int(cx+eig_vec2[0]*axis_length[0]/2),int(cy+eig_vec2[1]*axis_length[0]/2))
            
		    cv2.line(image,x11,x12,(0,0,255))
		    cv2.line(image,x21,x22,(0,0,255))
        except ValueError:
            print >>sys.stderr, "Single pixel star"
    return image

if __name__ == '__main__':
	for s in extract_stars(cv2.imread(sys.argv[1])):
		print str(s[0])+" "+str(s[1])+" "+str(s[2])
	
