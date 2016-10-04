from astropy.io import fits
from astropy import wcs
import numpy as np

hdulist = fits.open('../catalog_gen/calibration/image.axy')
results=np.array([[i['x'],i['y'],i['flux']] for i in hdulist[1].data])

#use astrometry calibration data to correct for image distortion
#see http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html
wcslist = fits.open('../catalog_gen/calibration/image.wcs')
w = wcs.WCS(wcslist[0].header)
results[:,0:2]=w.sip_pix2foc(results[:,0:2],1)

for i in results: print i[0],i[1],i[2]
