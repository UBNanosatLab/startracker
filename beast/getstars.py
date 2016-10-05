import numpy as np
import cv2
import time
from astropy import wcs
from astropy.io import fits
execfile("../catalog_gen/calibration/calibration.txt")

#use astrometry calibration data to correct for image distortion
#see http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html
wcslist = fits.open('../catalog_gen/calibration/image.wcs')
w = wcs.WCS(wcslist[0].header)
def extract_stars(input_file):
    """
    Takes in a picture and will extract the star x,y centroids as well as
    the value of the brightest pixel in each star

    Args:
        input_file: the file to be processed
    Returns:
        An array containing tuples of star info. Tuple format :(x,y,brightest value in star)

    """
    # 0 is the value used to read in an image in grey scale
    img = cv2.imread(input_file,0)
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
            stars.append((cx,cy,img[cy,cx]))

    #use astrometry calibration data to correct for image distortion
    #see http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html
    results=np.array(stars)
    results[:,0:2]=w.sip_pix2foc(results[:,0:2],1)
    return results

for i in extract_stars("polaris-1s-gain38-4.bmp"): print i[0],i[1],i[2]
