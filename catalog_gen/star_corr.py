from beast.getstars import *
from sys import stderr

execfile(PROJECT_ROOT+"catalog_gen/calibration/calibration.txt")


IMG_X=IMAGEW
IMG_Y=IMAGEH
DEG_X=FIELDW
DEG_Y=FIELDH

print "IMG_X="+str(IMG_X)
print "IMG_Y="+str(IMG_Y)
print "DEG_X="+str(DEG_X)
print "DEG_Y="+str(DEG_Y)


def xyz_points(image_stars_info):
    """
    Converts the (x,y,magnitude) values to x,y,z points
        Input:
            image_stars_info: list of tuples in the form (x,y,magnitude)
        Output:
            star_points: a list of tuples in the form (x,y,z)
    """
    star_points = []
    for pixel_x,pixel_y,mag in image_stars_info:
        #formula for converting from x,y, magnitude to x,y,z
        j=2*np.tan(DEG_X*np.pi/(180*2))*pixel_x/IMG_X #j=(x/z)
        k=2*np.tan(DEG_Y*np.pi/(180*2))*pixel_y/IMG_Y #k=y/z
        x=1./np.sqrt(j*j+k*k+1)
        y=j*x
        z=k*x
        star_points.append([x,y,z])
    return star_points

#def get_ref_magnitude():


if __name__ == '__main__':
#	get_ref_magnitude()
	"""
	Prints out the refrence magnitude and value of the star whose brightest
	pixel intensity is closest to the reference magnitude
	"""
	img = cv2.imread(PROJECT_ROOT+"catalog_gen/calibration/image.png")
	image_stars_info = extract_stars(img)
	#map x,y,z to hipparcos id
	star_ids =[]

	sd=np.array(stardb.values(),dtype = object)
	db=np.array(sd[:,4:7].tolist(),dtype=float)
	star_points=np.array(xyz_points(image_stars_info))
	
	#create rotation matrix to convert camera to celestial based on astrometry results
	if USE_WCS==1:
		cam2cel=rotation_matrix([1,0,0], math.radians(ORIENTATION))
		cam2cel=np.dot(cam2cel,rotation_matrix([0,1,0], math.radians(DEC_TANGENT)))
		cam2cel=np.dot(cam2cel, rotation_matrix([0,0,1], math.radians(-RA_TANGENT)))
	else:
		cam2cel=rotation_matrix([1,0,0], math.radians(ORIENTATION_CENTER))
		cam2cel=np.dot(cam2cel,rotation_matrix([0,1,0], math.radians(DEC_CENTER)))
		cam2cel=np.dot(cam2cel, rotation_matrix([0,0,1], math.radians(-RA_CENTER)))
	
	#search database for our stars
	star_points_cel=np.dot(star_points, cam2cel)
	result = searchxyz(db,star_points_cel,PIXSCALE*PSF_RADIUS/3600.0);
	#result = searchxyz(db,star_points_cel,PIXSCALE*1000/3600.0);

	smallest_diff = float("inf")
	REF_VAL = 0
	#find closest magnitude
	A=[]
	B=[]
	pixel_mag=[]
	dn = cv2.imread("drawn.png")
	for i in range(0,len(star_points)):
		for j in range(0,len(result[i])):
			star_match=sd[result[i][j]]
			star_match_cel=np.dot(star_match[4:7], np.transpose(cam2cel))
			if(MIN_MAG!=None):
				x=int((star_match_cel[1]/star_match_cel[0])*(IMG_X/2)/np.tan(DEG_X*np.pi/(180*2)))+IMG_X/2
				y=int((star_match_cel[2]/star_match_cel[0])*(IMG_Y/2)/np.tan(DEG_Y*np.pi/(180*2)))+IMG_Y/2
				if (star_match[1]<MIN_MAG):
					A+=[star_points[i].tolist()]
					B+=[star_match[4:7].tolist()]
					pixel_mag+=[[image_stars_info[i][2],star_match[1]]]
					print  >>stderr, image_stars_info[i],star_match[1],xyz_dist(star_points_cel[i],star_match[4:7])*3600/PIXSCALE
					cv2.circle(dn,(x,y),int(PSF_RADIUS),(255,0,0))
					diff=abs(star_match[1]-MIN_MAG)
					if diff<smallest_diff:
						REF_VAL= image_stars_info[i][2]
						smallest_diff = diff
						REF_MAG=star_match[1]
				else:
					if (star_match[1]<=7.5):
						cv2.circle(dn,(x,y),int(PSF_RADIUS),(0,255,0))
			else:
				if (star_match[9]==0):
					A+=[star_points[i].tolist()]
					B+=[star_match[4:7].tolist()]
					pixel_mag+=[[image_stars_info[i][2],star_match[1]]]
					diff=abs(image_stars_info[i][2]-IMAGE_STDEV*BRIGHT_ERR_SIGMA)
					if diff<smallest_diff:
						REF_VAL= image_stars_info[i][2]
						smallest_diff = diff
						REF_MAG=star_match[1]		
	cv2.imshow("dn",dn)
	cv2.waitKey()
	attitude_matrix=rigid_transform_3D(np.array(A),np.array(B))
	err=np.dot(A,attitude_matrix)-B
	#average error in arcseconds
	err=3600*np.degrees(np.sqrt(np.sum(err*err,1)))/PIXSCALE
	POS_ERR_STDEV=np.median(err)
	print "POS_ERR_STDEV="+str(POS_ERR_STDEV)
	print "REF_VAL="+str(int(REF_VAL))
	print "REF_MAG="+str(REF_MAG)
	print "ARC_ERR="+str(PIXSCALE*POS_ERR_STDEV*POS_ERR_SIGMA)
	print >>stderr,"Stars total: "+str(len(star_points))
	print >>stderr,"Stars used: "+str(len(A))
	#for i in range(0,len(err)):
	#	print pixel_mag[i],err[i]
	#BB=np.dot(np.linalg.pinv(np.dot(A,np.transpose(cam2cel))),np.dot(B,np.transpose(cam2cel)))
