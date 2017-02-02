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
images = np.empty(num_images, dtype=object)

for n in range(0, num_images):
	images[n] = cv2.imread( join(mypath,image_names[n]) ).astype(float)

mean_image=images[0]
for n in range(1, num_images):
	mean_image+=images[n]
mean_image/=num_images
mean_image = cv2.GaussianBlur(mean_image,(3,3),0)
cv2.imwrite(PROJECT_ROOT+"beast/mean_image.png",mean_image)

stdev_image=(images[0]-mean_image)**2
for n in range(1, num_images):
	stdev_image+=(images[n]-mean_image)**2
stdev_image=np.sqrt(stdev_image/(num_images-1))


IMAGE_STDEV=np.mean(stdev_image)
#1/(3e) chance a pixel will appear above the threshold
BRIGHT_ERR_SIGMA=poisson.ppf(1-(3.0*NUM_FALSE_PIXELS)/(len(stdev_image)),IMAGE_STDEV)/IMAGE_STDEV
print "IMAGE_STDEV="+str(IMAGE_STDEV)
print "BRIGHT_ERR_SIGMA="+str(BRIGHT_ERR_SIGMA)
