from astropy.io import fits
import numpy as np
import gendb
from itertools import chain
from config import PROJECT_ROOT


execfile(PROJECT_ROOT+"catalog_gen/calibration/calibration.txt")

def get_pos_err():
    """
    Determines the standard deviation of the star position error. The error is
    our captured distance versus the distance as noted in the star database. Prints
    the star position standard deviation to stdout
    """
<<<<<<< HEAD
    hdulist = fits.open(PROJECT_ROOT+'catalog_gen/calibration/image.corr')
    results=[(i['field_x']-i['index_x'])**2+(i['field_y']-i['index_y'])**2 for i in hdulist[1].data]
    POS_ERR_STDEV = np.sqrt(sum(results))/(2*(len(results)-1))
    print "POS_ERR_STDEV ", POS_ERR_STDEV

def ra_dec_to_xyz(ra_dec):
    """
    Converts right acension and declination to x,y,z coordinates
        Input:
            ra_dec: two element list in the form [ra,dec]
        Return:
            a list of the x,y,z coordinates in the form [x,y,z]
    """
    ra = ra_dec[0]
    dec = ra_dec[1]
    x=np.cos(np.radians(ra))*np.cos(np.radians(dec))
    y=np.sin(np.radians(ra))*np.cos(np.radians(dec))
    z=np.sin(np.radians(dec))
    return [x,y,z]
def get_ref_magnitude():
    """
    Prints out the refrence magnitude and value of the star whose brightest
    pixel intensity is closest to the reference magnitude
    """
    REF_MAG = 127
    hdulist = fits.open(PROJECT_ROOT+'catalog_gen/calibration/image.corr')
    ra_dec = [[i['index_ra'],i['index_dec']] for i in hdulist[1].data]
    xyz = [ra_dec_to_xyz(i) for i in ra_dec]
    radius = POS_ERR_STDEV*POS_ERR_SIGMA
    #map x,y,z to hipparcos id
    db = []
    star_ids =[]
    for k in gendb.stardb:
        xyz_pt = gendb.stardb[k][4:7]
        db.append(xyz_pt)
        star_ids.append(k)

    matched_indexes = gendb.searchxyz(db,xyz,radius);

    #flattens the 2D array and filters out duplicates
    matched_indexes = list(set(chain.from_iterable(matched_indexes)))

    smallest_diff = float("inf")
    REF_VAL = 0
    smallest_id = 0
    #find closest magnitude
    for i in matched_indexes:
        #7= index of MAX_BRIGHTNESS
        hip_id = star_ids[i]
        mag = gendb.stardb[hip_id][7]
        diff = np.absolute(REF_MAG-mag)
        if diff<smallest_diff:
            REF_VAL= mag
            smallest_diff = diff
            smallest_id = hip_id
    print "REF_VAL ",REF_VAL
    print "REF_MAG ",REF_MAG

if __name__ == '__main__':
    get_pos_err()
    get_ref_magnitude()
