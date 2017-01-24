from astropy.io import fits
import numpy as np
import gendb
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
    hdulist = fits.open(PROJECT_ROOT+'catalog_gen/calibration/image.corr')
    ra_dec_flux = [[i['index_ra'],i['index_dec'],i['FLUX']] for i in hdulist[1].data]
    xyz = [ra_dec_to_xyz(i) for i in ra_dec_flux]
    radius = POS_ERR_STDEV*POS_ERR_SIGMA/3600.0
    #map x,y,z to hipparcos id
    star_ids =[]

    sd=np.array(gendb.stardb.values(),dtype = object)
    db=np.array(sd[:,4:7].tolist(),dtype=float)

    result = gendb.searchxyz(db,xyz,radius);


    smallest_diff = float("inf")
    REF_VAL = 0
    smallest_id = 0
    #find closest magnitude
    for i in range(0,len(xyz)):
        if len(result[i])==1:
            diff=abs(ra_dec_flux[i][2]-127)
            if diff<smallest_diff:
                REF_VAL= ra_dec_flux[i][2]
                smallest_diff = diff
                smallest_id = result[i][0]
    REF_MAG=sd[smallest_id][1]
    print "REF_VAL="+str(int(REF_VAL))
    print "REF_MAG="+str(REF_MAG)

if __name__ == '__main__':
    get_ref_magnitude()
