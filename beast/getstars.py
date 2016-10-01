import numpy as np
import cv2

execfile("../catalog_gen/calibration/calibration.txt")
"""
Takes in a picture and will extract the star x,y centroids as well as
the value of the brightest pixel in each star

Args:
    input_file: the file to be processed
Returns:
    An array containing tuples of star info. Tuple format :(x,y,brightest value in star)

"""
def extract_stars(input_file):
    img = cv2.imread(input_file)
    gray_scale = cv2.cvtColor( img, cv2.COLOR_RGB2GRAY );
    #removes areas of the image that don't meet our brightness threshold
    ret,thresh = cv2.threshold(gray_scale,IMAGE_MEAN+IMAGE_STDEV*BRIGHTNESS_SIGMA,IMAGE_MAX,3)
    contours,heirachy = cv2.findContours(thresh,1,2);
    stars = []
    for c in contours:
        M = cv2.moments(c)
        if M['m00']>0:
            #this is how the x and y position are defined by cv2
            cx = M['m10']/M['m00']
            cy = M['m01']/M['m00']

            #these create a mask for the selected star that we are processing
            mask2 = np.zeros(gray_scale.shape[:2],np.uint8)
            cv2.drawContours(mask2,[c],-1,(255,255,255),3)


            hist = cv2.calcHist([img],[0],mask2,[256],[0,256])
            #finds the highest non-zero index in the histogram
            brightest_pixel = 0
            for i in range(len(hist)):
                if hist[i][0] !=0:
                    brightest_pixel = i
            stars.append((cx,cy,brightest_pixel))
    f = open("get_test.txt","wa")
    for i,j,k in stars:
        f.write(str(i)+" "+str(j) + " " +str(float(k))+"\n")
    return stars
