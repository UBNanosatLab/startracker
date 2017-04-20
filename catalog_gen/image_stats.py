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

#stars arent that big a deal, but leaving them out can't hurt (2% more accurate)
IMAGE_VARIANCE=np.ma.average((images-median_image)**2,weights=images<median_image)
#IMAGE_VARIANCE=np.var(images-median_image)

#set a threshold so that we have a PROB_FALSE_STAR chance of a star apearing above the threshold per image
BRIGHT_THRESH=poisson.ppf(1+np.log(1-PROB_FALSE_STAR)/(median_image.size/3.0),IMAGE_VARIANCE)+1-IMAGE_VARIANCE
print "IMAGE_VARIANCE="+str(IMAGE_VARIANCE)
print "BRIGHT_THRESH="+str(BRIGHT_THRESH)
