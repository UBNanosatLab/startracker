from beast.getstars import *
from os import path
from sys import stderr

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

filterunreliable()
sd=np.array(stardb.values(),dtype = object)
db=np.array(sd[:,4:7].tolist(),dtype=float)
def get_ref_magnitude(solved_file,outputimg=0):
	"""
	Prints out the refrence magnitude and value of the star whose brightest
	pixel intensity is closest to the reference magnitude
	"""
	img_path=PROJECT_ROOT+'beast/bg_sample/'
	img = cv2.imread(img_path+solved_file.split("/")[-1].split(".")[0]+".png")
	if (outputimg):
		image_stars_info,img = extract_stars(img,path.abspath(solved_file),1)
	else:
		image_stars_info = extract_stars(img,path.abspath(solved_file),0)
	#map x,y,z to hipparcos id

	star_points=np.array(xyz_points(image_stars_info))
	
	#create rotation matrix to convert camera to celestial based on astrometry results
	cam2cel=rotation_matrix([1,0,0], math.radians(ORIENTATION_CENTER))
	cam2cel=np.dot(cam2cel,rotation_matrix([0,1,0], math.radians(DEC_CENTER)))
	cam2cel=np.dot(cam2cel, rotation_matrix([0,0,1], math.radians(-RA_CENTER)))
	
	#search database for our stars
	star_points_cel=np.dot(star_points, cam2cel)
	result = searchxyz(db,star_points_cel,PIXSCALE*PSF_RADIUS/3600.0);
	#result = searchxyz(db,star_points_cel,PIXSCALE*1000/3600.0);

	#find closest magnitude
	A=[]
	B=[]
	
	db_val=[]
	img_val=[]
	for i in range(0,len(star_points)):
		for j in range(0,len(result[i])):
			star_match=sd[result[i][j]]
			star_match_cel=np.dot(star_match[4:7], np.transpose(cam2cel))
			A+=[star_points[i].tolist()]
			B+=[star_match[4:7].tolist()]
			img_val.append(image_stars_info[i][2])
			db_val.append(star_match[1])
			if (outputimg):
				#draw circles on matched stars
				x=int((star_match_cel[1]/star_match_cel[0])*(IMG_X/2)/np.tan(DEG_X*np.pi/(180*2)))+IMG_X/2
				y=int((star_match_cel[2]/star_match_cel[0])*(IMG_Y/2)/np.tan(DEG_Y*np.pi/(180*2)))+IMG_Y/2
				cv2.circle(img,(x,y),int(PSF_RADIUS),(0,255,0))
	if len(A)<2:
		return([],[],[])
	attitude_matrix=rigid_transform_3D(np.array(A),np.array(B))
	err=np.dot(A,attitude_matrix)-B
	#average error in arcseconds
	db_img_dist=3600*np.degrees(np.sqrt(np.sum(err*err,1)))/PIXSCALE
	
	if (outputimg):
		cv2.imshow("im",img)
		cv2.waitKey()
	return (db_val,img_val,db_img_dist.tolist())

if __name__ == '__main__':
	db_val=[]
	for i in range(1,len(sys.argv)):
		execfile(sys.argv[i])
		a,b,c=get_ref_magnitude(sys.argv[i])
		starsfound=len(a)
		if (starsfound>=2):
			db_val+=a
			
	#Choose a minimum magnitude so that our star catalog will have the same
	#median magnitude as our sample images
	#We do it like this because a lot of the dimmer matches are false positives
	
	MIN_MAG=np.sort(sd[:,1])[2*sum(sd[:,1]<np.median(db_val))]
	
	filterbrightness(MIN_MAG)
	#filterdoublestars()

	sd=np.array(stardb.values(),dtype = object)
	db=np.array(sd[:,4:7].tolist(),dtype=float)
	least_err=np.Inf
	bestimage=""
	img_val=[]
	db_img_dist=[]
	for i in range(1,len(sys.argv)):
		execfile(sys.argv[i])
		a,b,c=get_ref_magnitude(sys.argv[i],0)
		starsfound=len(a)
		if (starsfound>=2):
			err=np.mean(c)
			print >>stderr,"Stars found: "+str(starsfound)
			print >>stderr,"Average err: "+str(err)
			if least_err>err:
				least_err=err
				bestimage=sys.argv[i]
			img_val+=b
			db_img_dist+=[c[i]**2-IMAGE_VARIANCE/b[i] for i in range(0,len(c))]
	
	print "MIN_MAG="+str(MIN_MAG)
	POS_VARIANCE=max(np.mean(db_img_dist),0)
	print "POS_VARIANCE="+str(POS_VARIANCE)
	#ARC_ERR requires some explaination: 
	#we take the square root of the position variance due to catalog error + the
	#worst case position variance due to image noise, and 
	#divide the whole thing by square root of two to correct for a mistake in the code
	#the code treats total err as 2*individual error, when in fact it sqrt(2)*individual error
	#this also lets us avoid square roots in the performance critical inner loop
	print "ARC_ERR="+str(PIXSCALE*POS_ERR_SIGMA*(np.sqrt((POS_VARIANCE+IMAGE_VARIANCE/BRIGHT_THRESH)/2)))
	print "BESTCALIB='"+str(bestimage.split("/")[-1].split(".")[0])+"'"
	f = open(bestimage, "r")
	print f.read()
	f.close()
	
