import cv2
import numpy
import math
#getting the Histogram, sorting and filtering out top 1% of stars,then printing the mean.
def image_stats(image):
    img =cv2.imread(image,1)
    channels = [None]*3
    channels[0],channels[1],channels[2] = cv2.split(img)

    r = cv2.calcHist(channels[2],[2],None,[256],[0,256])
    g = cv2.calcHist(channels[1],[1],None,[256],[0,256])
    b = cv2.calcHist(channels[0],[0],None,[256],[0,256])
    histo = [0]*len(r)
    #Adding together green, blue and red
    for i in range(0,len(r)):
        histo[i] = (r[i] + g[i] + b[i])
    #multiplying by the weights

    top1 = numpy.percentile(histo,99)

    vals = []
    #Sorting out top 1% and adding pixal values to vals array
    for j in range(0,len(histo)):

        vals.append(j)
        if (histo[j] >= top1):
            histo[j] = 0


    n = int(sum(histo))

    numpy.asarray(histo)
    numpy.asarray(vals)

    IMAGE_MEAN = numpy.average(vals,weights=histo)
    varience = numpy.average((vals - IMAGE_MEAN)**2,weights = histo)

    varience = varience * (n/n-1)

    IMAGE_STDEV = math.sqrt(varience)


    print("IMAGE_MEAN : " + str(IMAGE_MEAN))
    print("IMAGE_STDEV : " + str(IMAGE_STDEV))
