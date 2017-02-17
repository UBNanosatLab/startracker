from beast.getstars import *
from os import path
from sys import stderr

def median_line(x,y):
	minerr=np.Inf
	for j in range(1,len(x)):
		for i in range(0,j):
			if x[j]!=x[i]:
				m=(y[j]-y[i])/(x[j]-x[i])
				b=y[j]-m*x[j]
				err=np.sum(np.abs(y-(np.multiply(m,x)+b)))
				if (err<minerr):
					minm=m
					minb=b
					minerr=err
	return (minm,minb)
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

sd=np.array(stardb.values(),dtype = object)
db=np.array(sd[:,4:7].tolist(),dtype=float)
def get_ref_magnitude(solved_file):
	"""
	Prints out the refrence magnitude and value of the star whose brightest
	pixel intensity is closest to the reference magnitude
	"""
	img_path=PROJECT_ROOT+'beast/bg_sample/'
	img = cv2.imread(img_path+solved_file.split("/")[-1].split(".")[0]+".png")
	image_stars_info,img = extract_stars(img,path.abspath(solved_file),1)
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
			if(MIN_MAG!=None):
				x=int((star_match_cel[1]/star_match_cel[0])*(IMG_X/2)/np.tan(DEG_X*np.pi/(180*2)))+IMG_X/2
				y=int((star_match_cel[2]/star_match_cel[0])*(IMG_Y/2)/np.tan(DEG_Y*np.pi/(180*2)))+IMG_Y/2
				if (star_match[1]<=MIN_MAG):
					A+=[star_points[i].tolist()]
					B+=[star_match[4:7].tolist()]
					img_val.append(image_stars_info[i][2])
					db_val.append(10**(star_match[1]/-2.5))
					#db_val.append(star_match[1])
					cv2.circle(img,(x,y),int(PSF_RADIUS),(255,0,0))
				else:
					cv2.circle(img,(x,y),int(PSF_RADIUS),(0,255,0))
			else:
				if (star_match[9]==0):
					A+=[star_points[i].tolist()]
					B+=[star_match[4:7].tolist()]
					img_val.append(image_stars_info[i][2])
					db_val.append(10**(star_match[1]/-2.5))
					#db_val.append(star_match[1])
	attitude_matrix=rigid_transform_3D(np.array(A),np.array(B))
	err=np.dot(A,attitude_matrix)-B
	#average error in arcseconds
	db_img_dist=3600*np.degrees(np.sqrt(np.sum(err*err,1)))/PIXSCALE
	cv2.imshow("im",img)
	cv2.waitKey()
	return (db_val,img_val,db_img_dist.tolist())

if __name__ == '__main__':
	least_err=np.Inf
	bestimage=""
	db_val=[]
	img_val=[]
	db_img_dist=[]
	for i in range(1,len(sys.argv)):
		execfile(sys.argv[i])
		a,b,c=get_ref_magnitude(sys.argv[i])
		starsfound=len(a)
		if (starsfound>=4):
			err=np.mean(c)
			print >>stderr,"Stars found: "+str(starsfound)
			print >>stderr,"Average err: "+str(err)
			if least_err>err:
				least_err=err
				bestimage=sys.argv[i]
			db_val+=a
			img_val+=b
			db_img_dist+=c
	MAG2VAL_M,MAG2VAL_B=median_line(db_val,img_val)
	#MAG2VAL_M,MAG2VAL_B=np.linalg.lstsq(np.vstack([db_val, np.ones(len(db_val))]).T,img_val)[0]
	#MAG2VAL_STDEV_M,MAG2VAL_STDEV_B=median_line(db_val,np.abs(img_val-(np.multiply(MAG2VAL_M,db_val)+MAG2VAL_B)))
	above=[]
	below=[]
	for i in img_val-(np.multiply(MAG2VAL_M,db_val)+MAG2VAL_B):
		if i>0:
			above.append(i)
		elif i<0:
			below.append(i)
	#from messing around, 65 seems good
	MAG2VAL_ABOVE=np.percentile(above,65)
	MAG2VAL_BELOW=np.percentile(below,65)
	import matplotlib.pyplot as plt
	plt.plot(db_val,img_val,'o')
	plt.plot(db_val, np.multiply(MAG2VAL_M,db_val)+MAG2VAL_B, 'r')
	plt.plot(db_val, np.multiply(MAG2VAL_M,db_val)+MAG2VAL_B+MAG2VAL_ABOVE*MAG_BOUND_SIGMA, 'g')
	plt.plot(db_val, np.multiply(MAG2VAL_M,db_val)+MAG2VAL_B+MAG2VAL_BELOW*MAG_BOUND_SIGMA, 'g')
	plt.show()

	POS_ERR_STDEV=np.median(db_img_dist)
	print "POS_ERR_STDEV="+str(POS_ERR_STDEV)
	print "ARC_ERR="+str(PIXSCALE*POS_ERR_STDEV*POS_ERR_SIGMA)
	print "MAG2VAL_M="+str(MAG2VAL_M)
	print "MAG2VAL_B="+str(MAG2VAL_B)
	print "MAG2VAL_ABOVE="+str(MAG2VAL_ABOVE)
	print "MAG2VAL_BELOW="+str(MAG2VAL_BELOW)
	print "BESTCALIB='"+str(bestimage.split("/")[-1].split(".")[0])+"'"
	f = open(bestimage, "r")
	print f.read()
	f.close()
