import cv2
import numpy as np
import math
def calc_stats(img):

    """Helper function for get_image_stats.
       This function calcuates the IMAGE_MEAN and IMAGE_STDEV

       Args:
       image: The image to be calculated


       Returns a tuple containing IMAGE_MEAN and IMAGE_STDEV respectively
    """


    r = cv2.calcHist([img],[2],None,[256],[0,256])
    g = cv2.calcHist([img],[1],None,[256],[0,256])
    b = cv2.calcHist([img],[0],None,[256],[0,256])
    histo = [0]*len(r)
    #Adding together green, blue and red

    histo=r[:,0]+g[:,0]+b[:,0]

    numpixels=img.size/3
    bottom99=numpixels*.99
    n=numpixels

    #Sorting out top 1%
    for j in range(len(histo)-1,-1,-1):
        n-=histo[j]
        histo[j] = 0
        if n<=bottom99:
            break

    vals = np.arange(0,256)

    IMAGE_MEAN = np.average(vals,weights=histo)
    varience = np.average((vals - IMAGE_MEAN)**2,weights = histo)
    varience = varience * n/(n-1)
    IMAGE_STDEV = math.sqrt(varience)
    return (IMAGE_MEAN,IMAGE_STDEV)
def get_image_stats(image):

    """ Takes in an image finds the Mean and Standard Deviation,
        blurs the image and recalulates the Mean and Standard Deviation

        Args:
        image: The image to be calculated



        Returns a tuple containing IMAGE_MEAN and IMAGE_STDEV respectively
    """
    execfile("calibration/calibration.txt")
    image='image.png'
    img =cv2.imread(image,1)
    run_1 = calc_stats(img)
    IMAGE_MEAN = run_1[0]
    IMAGE_STDEV = run_1[1]
    temp = []
    for row in img:
        temp.append([IMAGE_MEAN if j> IMAGE_MEAN + (IMAGE_STDEV * BRIGHT_ERR_SIGMA) else j for j in row])
    img = temp
    blur = cv2.GaussianBlur(img,(3,3),0)
    result = calc_stats(blur)
    IMAGE_MEAN = result[0]
    IMAGE_STDEV = result [1]
    print "IMAGE_MEAN=" + str(IMAGE_MEAN)
    print "IMAGE_STDEV=" + str(IMAGE_STDEV)
    print "PSF_RADIUS=" + str(3.5)
    return(IMAGE_MEAN,IMAGE_STDEV)
