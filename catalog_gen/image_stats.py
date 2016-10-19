import cv2
import numpy as np
import math
execfile("calibration.txt")
#getting the Histogram, sorting and filtering out top 1% of stars,then printing the mean.
def get_image_stats(image='image.png'):

    """ Takes in an image finds the Mean and Standard Deviation,
        blurs the image and recalulates the Mean and Standard Deviation

        Args:
        image: The image to be calculated

        Returns a tuple containing IMAGE_MEAN and IMAGE_STDEV respectively
    """
    img =cv2.imread(image,1)
    r = cv2.calcHist([img],[2],None,[256],[0,256])
    g = cv2.calcHist([img],[1],None,[256],[0,256])
    b = cv2.calcHist([img],[0],None,[256],[0,256])
    histo = [0]*len(r)
    #Adding together green, blue and red
    
    histo=r[:,0]+g[:,0]+b[:,0]
    #multiplying by the weights
    #histo.sort()
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

(IMAGE_MEAN,IMAGE_STDEV)=get_image_stats()
print "IMAGE_MEAN=" + str(IMAGE_MEAN)
print "IMAGE_STDEV=" + str(IMAGE_STDEV)
print "PSF_RADIUS=" + str(3.5)