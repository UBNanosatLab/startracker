from astropy.io import fits
from astropy import wcs
import numpy as np

hdulist = fits.open('../catalog_gen/calibration/image.corr')
#print ','.join([hdulist[1].header['TTYPE'+str(i)] for i in range (1,14)])

#field_x,field_y,field_ra,field_dec,index_x,index_y,index_ra,index_dec,index_id,field_id,match_weight,FLUX,BACKGROUND

#description:

#field_x,field_y,field_ra,field_dec - describe the position and celestial coordinates of the star in our image
#index_x,index_y,index_ra,index_dec - describe the position and celestial coordinates of the star as predicted by the star catalog
#index_id,field_id - some internal astrometry thing
#match_weight - how much weight to give to this star in determining sttitude (see the wikipedia page on Wahba's problem)
#FLUX - maximum pixel brightness value of the star
#BACKGROUND - brightness of the area around the star

results=np.array([[i['index_x'],i['index_y'],i['flux']] for i in hdulist[1].data])

#use astrometry calibration data to correct for image distortion
#see http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html
wcslist = fits.open('../catalog_gen/calibration/image.wcs')
w = wcs.WCS(wcslist[0].header)
results[:,0:2]=w.sip_pix2foc(results[:,0:2],1)

for i in results: print i[0],i[1],i[2]
