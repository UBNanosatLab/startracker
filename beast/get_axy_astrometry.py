from astropy.io import fits
hdulist = fits.open('../catalog_gen/calibration/image.axy')
for i in hdulist[1].data: print i['x'],i['y'],i['flux']
