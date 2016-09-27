from astropy.io import fits
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

for i in hdulist[1].data: print i['field_x'],i['field_y'],i['flux']
