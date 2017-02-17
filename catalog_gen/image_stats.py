from os import listdir
from os.path import isfile, join
import cv2
import numpy as np
import math
from config import PROJECT_ROOT
from scipy.stats import poisson

execfile(PROJECT_ROOT+"catalog_gen/calibration/calibration.txt")

mypath=PROJECT_ROOT+'beast/bg_sample'
image_names = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
num_images=len(image_names)

images = np.asarray([cv2.imread( join(mypath,image_names[n]) ).astype(float) for n in range(0, num_images)])
median_image=np.median(images,axis=0)
#median_image = cv2.GaussianBlur(median_image,(3,3),0)
cv2.imwrite(PROJECT_ROOT+"beast/median_image.png",median_image)

#filter the background image for astrometry - more important for starfield generator
for n in range(0, num_images):
	cv2.imwrite("calibration/"+image_names[n],np.clip(images[n]-median_image,a_min=0,a_max=255).astype(np.uint8))

#median is robust to stars, so use that rather than mean to calculate variance
#use the experementally determined percentile value of 70 to make it come out like it would have if we had used median
IMAGE_VARIANCE=np.percentile([(n-median_image)**2 for n in images],70)
BRIGHT_ERR_SIGMA=poisson.ppf(1-(3.0*NUM_FALSE_PIXELS)/(median_image.size),IMAGE_VARIANCE)/IMAGE_VARIANCE
print "IMAGE_VARIANCE="+str(IMAGE_VARIANCE)
print "BRIGHT_ERR_SIGMA="+str(BRIGHT_ERR_SIGMA)
