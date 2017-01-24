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
	images[n] = cv2.GaussianBlur(cv2.imread( join(mypath,image_names[n]) ),(3,3),0).astype(float)
	#images[n] = cv2.imread( join(mypath,image_names[n]) ).astype(float)
	#images[n] = cv2.imread( join(mypath,image_names[n]) )

mean_image=images[0]
for n in range(1, num_images):
	mean_image+=images[n]
mean_image/=num_images

cv2.imwrite(PROJECT_ROOT+"beast/mean_image.png",mean_image)

stdev_image=(images[0]-mean_image)**2
for n in range(1, num_images):
	stdev_image+=(images[n]-mean_image)**2
stdev_image=np.sqrt(stdev_image/(num_images-1))


IMAGE_STDEV=np.max(stdev_image)
#1/1000.0 = chance that an image will contain a pixel above the threshold
BRIGHT_ERR_SIGMA=poisson.ppf(1-1/(1000.0),np.max(stdev_image))/np.max(stdev_image)
print "IMAGE_STDEV="+str(IMAGE_STDEV)
print "BRIGHT_ERR_SIGMA="+str(BRIGHT_ERR_SIGMA)
