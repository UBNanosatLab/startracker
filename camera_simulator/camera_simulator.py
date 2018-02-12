# -*- coding: utf-8 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
import socket
from datetime import datetime
from time import time, sleep, gmtime
from pygame.locals import *
import sys, os, math
import numpy as np

if sys.platform == 'win32' or sys.platform == 'win64':
	os.environ['SDL_VIDEO_CENTERED'] = '1'
dir='Data'
sys.path.append(dir)
import Objects
import sidereal

pygame.init()
Objects.main()

prev_body2ECI=np.eye(3)
curr_body2ECI=np.eye(3)
prev_updatetime=0
curr_updatetime=1
last_ts=0
last_ts_time=time()

#host = 'jeb.eng.buffalo.edu' 
host = 'jeb' 
port = 7008 
size = 16384

#view_distance = 5*6781000/6367444.7 #5*orbit height/ earth radius
view_angle = [0.0, 0.0,0.0]
longitude_offset=0.0


from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

#target = twoline2rv('1 21639U 91054B   16187.52939780  .00000067  00000-0  00000+0 0  9998',
#'2 21639  14.1200  25.1672 0023264 335.9153 306.1103  1.00282119 91277',
#wgs72) #TDRS 5.tle

target = twoline2rv('1 22314U 93003B   16093.41138873 -.00000292  00000-0  00000+0 0  9994',
'2 22314  13.5307  29.0726 0006519 302.6439 321.7503  1.00273121 84995',
wgs72) #TDRS 6.tle

glados = twoline2rv('1 25544U 98067A   16188.56972458  .00002764  00000-0  47951-4 0  9999',
'2 25544  51.6437 321.3331 0001117  43.2597  53.1206 15.54721465  8009',
wgs72) #ISS.tle

def a2q(A):
	q4=0.5*np.sqrt(1+np.trace(A));

	q1=1/(4*q4)*(A[1,2]-A[2,1]);
	q2=1/(4*q4)*(A[2,0]-A[0,2]);
	q3=1/(4*q4)*(A[0,1]-A[1,0]);

	return np.array([q1,q2,q3,q4])

def q2a(q):
	return np.array([[q[0]**2-q[1]**2-q[2]**2+q[3]**2,2*(q[0]*q[1]+q[2]*q[3]),2*(q[0]*q[2]-q[1]*q[3])],[2*(q[0]*q[1]-q[2]*q[3]),-q[0]**2+q[1]**2-q[2]**2+q[3]**2,2*(q[1]*q[2]+q[0]*q[3])],[2*(q[0]*q[2]+q[1]*q[3]),2*(q[1]*q[2]-q[0]*q[3]),-q[0]**2-q[1]**2+q[2]**2+q[3]**2]])

def interpolate_matrix(present_time):
        A=prev_body2ECI
        B=curr_body2ECI

        t1=prev_updatetime
        t2=curr_updatetime
        t3=present_time

	# Calculate error angles between A and B via small angle approximation
	# of MRPs.
	R=np.dot(B,np.transpose(A))
	dq=a2q(R)
	dp=np.array([dq[0],dq[1],dq[2]])/(1 + dq[3])
	anglesAB=4*dp

	# Extrapolate to new error angles between B and C.
	anglesBC=anglesAB/(t2-t1)*(t3-t2)

	# Convert to a quaternion via small angle approximation, then get C.
	C=np.dot(q2a(np.array([0.5*anglesBC[0],0.5*anglesBC[1],0.5*anglesBC[2],1])),B)

	return C

def rotation_matrix(axis, theta):
	"""
	Return the rotation matrix associated with counterclockwise rotation about
	the given axis by theta radians.
	"""
	axis = np.asarray(axis)
	axis = axis/math.sqrt(np.dot(axis, axis))
	a = math.cos(theta/2.0)
	b, c, d = -axis*math.sin(theta/2.0)
	aa, bb, cc, dd = a*a, b*b, c*c, d*d
	bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
	return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],[2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],[2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

def draw():
	global prev_body2ECI
	global curr_body2ECI
	global prev_updatetime
	global curr_updatetime
	global last_ts
	global last_ts_time

	#RESET ALL----------------------------------------
	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
	while True:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host,port))
		data = s.recv(size).split()
		s.close()
		if len(data)!=14:
			print "got "+str(len(data))+" fields, expected 14"
			n=1
			for i in data:
				print "field",n,i
				n=n+1
			sleep(.01)
			continue
		break

	#TODO: reconcile px->y reconcile py->z with ADC px->x py->y
	for i in range(0,len(data)):
		print i,len(data[i].split(",")),data[i]

	body2ECI=np.transpose(np.array(data[8].split(",")).astype(np.float).reshape((3, 3)))
	#y and z axis are flipped in the startracker so we need to apply an extra correction
	body2ECI=np.transpose(np.dot(np.array([[0,0,1],[1,0,0],[0,1,0]]), body2ECI))

	#new update from simulation server
	if (float(data[12])!=curr_updatetime):
		prev_updatetime=curr_updatetime
		curr_updatetime=float(data[12])
		prev_body2ECI=curr_body2ECI
		curr_body2ECI=body2ECI

	body2ECI=interpolate_matrix(min(float(data[13]),2*curr_updatetime-prev_updatetime))

	DEC=np.degrees(np.arcsin(body2ECI[2,0]))+view_angle[0]
	RA=np.degrees(np.arctan2(body2ECI[1,0],body2ECI[0,0]))+view_angle[1]
	ORIENTATION=np.degrees(np.pi-np.arctan2(body2ECI[2,1],body2ECI[2,2]))+view_angle[2]

	print >>sys.stderr, "DEC="+str(DEC)
	print >>sys.stderr, "RA="+str(RA)
	print >>sys.stderr, "ORIENTATION="+str(ORIENTATION)

	#print data
	latitude=float(data[0].split(",")[0])
	longitude=float(data[0].split(",")[1])
	altitude=float(data[0].split(",")[2])
	ts=float(data[0].split(",")[3])
	if (last_ts!=ts):
		last_ts=ts
		last_ts_time=time()
	ts_err=min(time()-last_ts_time,1.0)
	t2=gmtime(ts)
	target_position, target_velocity  = target.propagate(t2[0],t2[1],t2[2],t2[3],t2[4],t2[5]+ts_err)
	glados_position, glados_velocity  = glados.propagate(t2[0],t2[1],t2[2],t2[3],t2[4],t2[5]+ts_err)
	ts=ts+ts_err
	print "TS="+str(ts)
	print "Target Position "+str(target_position)
	print "GLADOS Position "+str(glados_position)
	target_rel_pos=np.array(target_position)-np.array(glados_position)
	target_rel_pos=target_rel_pos/np.linalg.norm(target_rel_pos)

	TARGET_DEC=np.degrees(np.arcsin(target_rel_pos[2]))
	#rotation about the z axis (-180 to +180)
	TARGET_RA=np.degrees(np.arctan2(target_rel_pos[1],target_rel_pos[0]))

	print 'TARGET_DEC='+str(TARGET_DEC)
	print 'TARGET_RA='+str(TARGET_RA)

	#Buffalo
	#latitude = 42.886448
	#longitude = -78.878372 

	glados_position_norm=np.array(glados_position)
	glados_position_norm=glados_position_norm/np.linalg.norm(glados_position_norm)
	ra_earth=np.degrees(np.arctan2(glados_position_norm[1],glados_position_norm[0]))
	dec_earth=np.degrees(np.arcsin(glados_position_norm[2]))
	longitude+=longitude_offset
	view_distance = np.sqrt(glados_position[0]*glados_position[0]+glados_position[1]*glados_position[1]+glados_position[2]*glados_position[2])*5/6367.4447 #5*orbit height/ earth radius
	glLoadIdentity()
	glDisable(GL_LIGHTING)

	#point the camera at the target ra and dec
	glRotatef(DEC, -1.0, 0.0, 0.0)
	glRotatef(RA, 0.0, -1.0, 0.0)
	x=np.cos(np.radians(RA))*np.cos(np.radians(DEC))
	y=np.sin(np.radians(RA))*np.cos(np.radians(DEC))
	z=np.sin(np.radians(DEC))

	glRotatef(ORIENTATION-180, -y, z, -x)

	#point the camera at the target ra and dec
	glPushMatrix()
	glRotatef(TARGET_RA, 0.0, 1.0, 0.0)
	glRotatef(TARGET_DEC, 1.0, 0.0, 0.0)

	glTranslatef(0,0,-3)
	glRotatef(90, 0,1,0)
	glRotatef((ts*11.0)%360, 0,0,1)

	glCallList(3)
	glPopMatrix()

	#map calculated sky ra and dec to the given latitude and longitude on earth
	glPushMatrix()
	glRotatef(ra_earth, 0.0, 1.0, 0.0)
	glRotatef(dec_earth, 1.0, 0.0, 0.0)
	glRotatef(90, 1.0, 0.0, 0.0)
	glTranslatef(0.0, view_distance, 0)

	#position the satelite directly above the desired latitude and longitude
	glRotatef(latitude, 1.0, 0.0, 0.0)
	glRotatef(longitude, 0.0, 0.0, -1.0)
	#Draw earth
	glCallList(1)
	glPopMatrix()

	# Draw the skybox
	glDepthMask(False)

	glCallList(2)
	#draw target

	# Re-enable lighting and depth test before we redraw the world
	glEnable(GL_LIGHTING)
	glDepthMask(True)

	# Here is where we would draw the rest of the world in a game
	pygame.display.flip()
def get_input():
	global view_distance, view_angle,longitude_offset,showEarth
	keystate = pygame.key.get_pressed()
	for event in pygame.event.get():
		if event.type == pygame.QUIT or keystate[K_ESCAPE]:
			pygame.quit(); sys.exit()
	if keystate[K_PAGEUP]:
		view_angle[2] += 1.0
	if keystate[K_PAGEDOWN]:
		view_angle[2] -= 1.0
	if keystate[K_RIGHT]: view_angle[1] -= 1.0
	if keystate[K_LEFT]: view_angle[1] += 1.0
	if keystate[K_UP]: view_angle[0] += 1.0
	if keystate[K_DOWN]: view_angle[0] -= 1.0
	if keystate[K_SPACE]: showEarth = 1-showEarth
	#if keystate[K_UP] and view_angle[0] < 90: view_angle[0] += 1.0
	#if keystate[K_DOWN] and view_angle[0] > -90: view_angle[0] -= 1.0

def main():
	curtime=time()
	while True:
		os.system("clear")
		get_input()
		draw()
		#sleep(.25)
		lasttime=curtime
		curtime=time()
		print "fps: "+str(1.0/(curtime-lasttime))
if __name__ == "__main__": main()
