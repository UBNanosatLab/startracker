from startracker import *
from config import PROJECT_ROOT
from astropy.io import fits
from astropy import wcs

def cal_xy_flux():
	hdulist = fits.open(PROJECT_ROOT+"catalog_gen/calibration/"+BESTCALIB+".corr")
	#print ','.join([hdulist[1].header['TTYPE'+str(i)] for i in range (1,14)])
	
	#field_x,field_y,field_ra,field_dec,index_x,index_y,index_ra,index_dec,index_id,field_id,match_weight,FLUX,BACKGROUND
	
	#description:
	
	#field_x,field_y,field_ra,field_dec - describe the position and celestial coordinates of the star in our image
	#index_x,index_y,index_ra,index_dec - describe the position and celestial coordinates of the star as predicted by the star catalog
	#index_id,field_id - some internal astrometry thing
	#match_weight - how much weight to give to this star in determining attitude (see the wikipedia page on Wahba's problem)
	#FLUX - maximum pixel brightness value of the star
	#BACKGROUND - brightness of the area around the star
	
	#results=np.array([[i['index_x'],i['index_y'],i['flux']] for i in hdulist[1].data])
	results=np.array([[i['field_x'],i['field_y'],i['flux']] for i in hdulist[1].data])
	
	#use astrometry calibration data to correct for image distortion
	#see http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html
	#APPARENTLY THIS DOESN'T WORK
	wcslist = fits.open(PROJECT_ROOT+"catalog_gen/calibration/"+BESTCALIB+".wcs")
	w = wcs.WCS(wcslist[0].header)
	results[:,0:2]=w.sip_pix2foc(results[:,0:2],1)
	
	return results

image_stars_info = [[i[0],i[1],i[2]] for i in cal_xy_flux()]
sq=identify_stars(image_stars_info)
if (len(sq)>0):
	A=np.array([[i[2],i[3],i[4]] for i in sq])
	B=np.array([[i[5],i[6],i[7]] for i in sq])
	R=rigid_transform_3D(A,B)
