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
	star_ids=[]
	try:
		star_query.flip()
		for i in image_stars_info:
			star_query.add_star(i[0],i[1],i[2])
		if (star_query.search()>0.99):
			star_ids = [[1/(POS_VARIANCE+IMAGE_VARIANCE/image_stars_info[i,2]), i,star_query.winner_id_map[i]] for i in range(0,len(star_query.winner_id_map)) if star_query.winner_id_map[i]!=-1]
	except NoMatchesFound:
		return []
		
	return [star_points[i[1]]+stardb[i[2]][4:7]+i for i in star_ids]


def do_solve(image_stars_info,txt_name):
		starttime=time()
		star_points=xyz_points(image_stars_info)
		sq=identify_stars(image_stars_info,star_points)
		
		f = open(txt_name,'a')
		data=star_query.search_rel()
		print >>f, data
		print >>f, [i for i in star_query.winner_id_map]
		f.close()
		
		if len(sq)>1:
			A=np.array([[i[0],i[1],i[2]] for i in sq])
			B=np.array([[i[3],i[4],i[5]] for i in sq])
			weights=np.array([i[6] for i in sq])
			R=rigid_transform_3D(A,B,weights)
			#R2=np.array([[star_query.R11,star_query.R12,star_query.R13],[star_query.R21,star_query.R22,star_query.R23],[star_query.R31,star_query.R32,star_query.R33]])
			#body2ECI_RA_DEC_ORI(R2)
		print "Time: "+str(time() - starttime)
		sys.stdout.flush()
		return i
		
if __name__ == '__main__':
	if len(sys.argv)==2:
		import socket,select, os
		epoll = select.epoll()
		server_ir=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_ir.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_ir.bind(('127.0.0.1', int(sys.argv[1])))
		server_ir.listen(5)
		server_ir.setblocking(0)
		epoll.register(server_ir.fileno(), select.EPOLLIN)

		server_rgb=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_rgb.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_rgb.bind(('127.0.0.1', int(sys.argv[2])))
		server_rgb.listen(5)
		server_rgb.setblocking(0)
		epoll.register(server_rgb.fileno(), select.EPOLLIN)

		conn_rgb_fd=-1
		conn_ir_fd=-1
		image_stars_info = []
		image_ir=[]
		image_rgb=[]

		txt_name=''
		while True:
			events = epoll.poll()
			for fd, event_type in events:
				if fd==server_ir.fileno():
					conn_ir, addr=server_ir.accept()
					conn_ir_fd=conn_ir.fileno()
					epoll.register(conn_ir_fd, select.EPOLLIN)
				if fd==conn_ir_fd:
					if (event_type&select.EPOLLIN)>0:
						img_name = os.read(conn_ir_fd, 1024)
						txt_name=img_name+'.txt'
						if len(data)>0:
							image_ir=cv2.imread(img_name)
							image_stars_info = extract_stars(cv2.imread(img_name))
							i=solve_img(image_stars_info,img_name)
							output_ir=data=" ".join([str(i[0])+","+str(i[1])+","+str(i[2])+","+str(i[3])+","+str(i[4])+","+str(i[5])+","+str(i[6]) for i in sq])
							os.write(conn_ir_fd, output_ir)
						else:
							epoll.unregister(conn_ir_fd)
							conn_ir.close()
							conn_ir_fd=-1

				if fd==server_rgb.fileno():
					conn_rgb, addr=server_rgb.accept()
					conn_rgb_fd=conn_rgb.fileno()
					epoll.register(conn_rgb_fd, select.EPOLLIN)
				if fd==conn_rgb_fd:
					if (event_type&select.EPOLLIN)>0:
						img_name = os.read(conn_rgb_fd, 1024)
						if len(data)>0:
							image_rgb=cv2.imread(img_name)
							#TODO: relative matching between rgb and ir image (since the cameras are probably not perfectly aligned)
							cx=image_stars_info[:,0]+IMG_X/2
							cy=image_stars_info[:,1]+IMG_Y/2
							
							f = open(txt_name,'a')
							print >>f, cv2.getRectSubPix(image_ir,(1,1),(cx,cy))
							print >>f, cv2.getRectSubPix(image_rgb,(1,1),(cx,cy))
							f.close()
							
							os.write(conn_rgb_fd,txt_name)
						else:
							epoll.unregister(conn_rgb_fd)
							conn_rgb.close()
							conn_rgb_fd=-1

	else:
		while True:
			try:
				img_name=raw_input().rstrip()
				if (img_name==''): break
				print img_name
				image_stars_info = extract_stars(cv2.imread(img_name))
				do_solve(image_stars_info,'/dev/stdout')
			except EOFError:
				break
