from astropy.io import fits
hdulist = fits.open('../catalog_gen/calibration/image.corr')
#print ','.join([hdulist[1].header['TTYPE'+str(i)] for i in range (1,14)])
#field_x,field_y,field_ra,field_dec,index_x,index_y,index_ra,index_dec,index_id,field_id,match_weight,FLUX,BACKGROUND
for i in hdulist[1].data: print i['field_x'],i['field_y'],i['flux']
#for i in hdulist[1].data: print i['index_x'],i['index_y'],i['flux']
