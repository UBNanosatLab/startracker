from astropy.io import fits
import numpy as np
from itertools import chain
from config import PROJECT_ROOT

def get_pos_err():
    """
    Determines the standard deviation of the star position error. The error is
    our captured distance versus the distance as noted in the star database. Prints
    the star position standard deviation to stdout
    """
    hdulist = fits.open(PROJECT_ROOT+'catalog_gen/calibration/image.corr')
    results=[(i['field_x']-i['index_x'])**2+(i['field_y']-i['index_y'])**2 for i in hdulist[1].data]
    POS_ERR_STDEV = np.sqrt(sum(results))/(2*(len(results)-1))
    print np.sqrt(results)
    print "POS_ERR_STDEV="+str( POS_ERR_STDEV)
if __name__ == '__main__':
    get_pos_err()
