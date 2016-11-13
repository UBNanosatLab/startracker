from astropy.io import fits
import numpy as np
import gendb
from itertools import chain
from config import PROJECT_ROOT


execfile(PROJECT_ROOT+"catalog_gen/calibration/calibration.txt")

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
    print "REF_VAL="+str(REF_VAL)
    print "REF_MAG="+str(REF_MAG)

if __name__ == '__main__':
    get_ref_magnitude()
