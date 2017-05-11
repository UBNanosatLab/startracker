from getstars import *
import beast
import datetime
from time import time
beast.load_db()
star_query=beast.star_query()
import socket

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

def group_stars(star_points ,false_stars = MAX_FALSE_STARS):
	if (len(star_points)<4):
		raise NoMatchesFound("Not enough stars")
	if (len(star_points)-4<false_stars):
		false_stars=len(star_points)-4
	star_kd = spatial.cKDTree(star_points)
	#arbitrarily chosen
	#second retval is the star array locations in tree.data
	results = star_kd.query(star_points,false_stars+4)
	return results[1]


def identify_stars(image_stars_info,star_points=[]):
	"""
	Takes in a list with star tuples of the form (x,y,mag) and attempts 
	to determine the attitude matrix that would transfrom the stars from the image
	to their locations in the database

	Input:
		image_stars_info: list of star tuples of the form (x,y,mag)
		star_points (optional): precomputed x,y,z values of image_stars_info
	Returns:
		matched_stars: database of stars that were matched in the form
	[im_x,im_y,im_z,db_x,db_y,db_z,weight,im_id,db_id]
	Raises:
		NoMatchesFound:
	"""
	global star_query
	#give the option to pass in precomputed star points, but dont require it
	if (len(star_points)==0):
		star_points = xyz_points(image_stars_info)

	image_stars_info=np.array(image_stars_info)
	try:
		star_query.flip()
		for i in image_stars_info:
			star_query.add_star(i[0],i[1],i[2])
		if (star_query.search()>0.99):
			star_ids = [[1/(POS_VARIANCE+IMAGE_VARIANCE/image_stars_info[i,2]), i,star_query.winner_id_map[i]] for i in range(0,len(star_query.winner_id_map)) if star_query.winner_id_map[i]!=-1]
	except NoMatchesFound:
		return []
		
	return [star_points[i[1]]+stardb[i[2]][4:7]+i for i in star_ids]

if __name__ == '__main__':
	if len(sys.argv)>1:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("127.0.0.1", sys.argv[1]))
		s.listen(1)
	while True:
		try:
			if len(sys.argv)>1:
				conn, addr = s.accept()
				img_name = conn.recv(1024).rstrip()
			else:
				img_name=raw_input().rstrip()
		except EOFError:
			break
		if (img_name==''): break
		starttime=time()
		image_stars_info = extract_stars(cv2.imread(img_name))
		star_points=xyz_points(image_stars_info)
		sq=identify_stars(image_stars_info,star_points)
		if len(sq)>1:
			A=np.array([[i[0],i[1],i[2]] for i in sq])
			B=np.array([[i[3],i[4],i[5]] for i in sq])
			weights=np.array([i[6] for i in sq])
			R=rigid_transform_3D(A,B,weights)
			#R2=np.array([[star_query.R11,star_query.R12,star_query.R13],[star_query.R21,star_query.R22,star_query.R23],[star_query.R31,star_query.R32,star_query.R33]])
			body2ECI_RA_DEC_ORI(R2)
		print img_name
		print "Time: "+str(time() - starttime)
		sys.stdout.flush()
		data=" ".join([str(i[0])+","+str(i[1])+","+str(i[2])+","+str(i[3])+","+str(i[4])+","+str(i[5])+","+str(i[6]) for i in sq])
		if len(sys.argv)>1:
			conn.sendall(data+"\r\n")
			conn.close()
