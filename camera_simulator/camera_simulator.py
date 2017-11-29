# -*- coding: utf-8 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
import socket
from datetime import datetime
from time import time, sleep, gmtime
from pygame.locals import *
import sys, os
import numpy as np

if sys.platform == 'win32' or sys.platform == 'win64':
	os.environ['SDL_VIDEO_CENTERED'] = '1'
dir='Data'
sys.path.append(dir)
import Objects
import sidereal

pygame.init()
Objects.main()

host = 'jeb.eng.buffalo.edu' 
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
	
def draw():
	latitude = 42.886448
	longitude = -78.878372 
	#RESET ALL----------------------------------------
	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
	while True:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host,port)) 
		data = s.recv(size).split()
		s.close()
		if len(data)!=12:
			continue
		break
	body2ECI=np.array(data[8].split(",")).astype(np.float).reshape((3, 3))
	#rotation about the y axis (-90 to +90)
	DEC=np.degrees(np.arcsin(body2ECI[0,2]))+view_angle[0]
	#rotation about the z axis (-180 to +180)
	RA=np.degrees(np.arctan2(body2ECI[0,1],body2ECI[0,0]))+view_angle[1]
	#rotation about the camera axis (-180 to +180)
	ORIENTATION=np.degrees(-np.arctan2(body2ECI[1,2],body2ECI[2,2]))+view_angle[2]
	#DEC=60
	#RA=150
	#ORIENTATION=-20
	print >>sys.stderr, "DEC="+str(DEC)
	print >>sys.stderr, "RA="+str(RA)
	print >>sys.stderr, "ORIENTATION="+str(ORIENTATION)
	#print data
	latitude=float(data[0].split(",")[0])
	longitude=float(data[0].split(",")[1])
	altitude=float(data[0].split(",")[2])
	ts=float(data[0].split(",")[3])
	t2=gmtime(ts)
	target_position, target_velocity  = target.propagate(t2[0],t2[1],t2[2],t2[3],t2[4],t2[5])
	glados_position, glados_velocity  = glados.propagate(t2[0],t2[1],t2[2],t2[3],t2[4],t2[5])
	target_rel_pos=np.array(target_position)-np.array(glados_position)
	target_rel_pos=target_rel_pos/np.linalg.norm(target_rel_pos)

	TARGET_DEC=np.degrees(np.arcsin(target_rel_pos[2]))
	#rotation about the z axis (-180 to +180)
	TARGET_RA=np.degrees(np.arctan2(target_rel_pos[1],target_rel_pos[0]))
	
	print 'TARGET_DEC='+str(TARGET_DEC)
	print 'TARGET_RA='+str(TARGET_RA)

	if altitude < 0.0:
		latitude=-latitude
		longitude=(longitude+360)%360-180

	utc = datetime.fromtimestamp(ts)
	gst = sidereal.SiderealTime.fromDatetime ( utc )
	lst = gst.lst(longitude)
	ra_earth  = sidereal.hoursToRadians(lst.hours%24.0)
	#ra_earth = 180
	dec_earth = latitude
	#dec_earth = 0
	longitude+=longitude_offset
	#print data
	#view_distance = 6*altitude/6367444.7 #5*orbit height/ earth radius
	view_distance = np.sqrt(glados_position[0]*glados_position[0]+glados_position[1]*glados_position[1]+glados_position[2]*glados_position[2])*5/6367.4447 #5*orbit height/ earth radius
	glLoadIdentity()
	glDisable(GL_LIGHTING)




	#point the camera at the target ra and dec
	glRotatef(DEC, -1.0, 0.0, 0.0)
	glRotatef(RA, 0.0, -1.0, 0.0)
	x=np.cos(np.radians(RA))*np.cos(np.radians(DEC))
	y=np.sin(np.radians(RA))*np.cos(np.radians(DEC))
	z=np.sin(np.radians(DEC))

	glRotatef(ORIENTATION+180, -y, z, -x)

	#point the camera at the target ra and dec
	glPushMatrix()
#	glRotatef(TARGET_DEC, 1.0, 0.0, 0.0)
#	glRotatef(TARGET_RA, 0.0, 1.0, 0.0)
	glRotatef(ORIENTATION+180, y, -z, x)
	glRotatef(TARGET_RA, 0.0, 1.0, 0.0)
	glRotatef(TARGET_DEC, 1.0, 0.0, 0.0)

	glTranslatef(0,0,-3)
	glRotatef(90, 0,1,0)
	glRotatef(ts%360, 0,0,1)

	glCallList(3)
	glPopMatrix()



	#map calculated sky ra and dec to the given latitude and longitude on earth
	glPushMatrix()
	glRotatef(dec_earth, 1.0, 0.0, 0.0)
	glRotatef(ra_earth, 0.0, 1.0, 0.0)
	print "ra_earth: "+str(ra_earth)
	print "dec_earth: "+str(dec_earth)
	glPushMatrix()
	glRotatef(90, 1.0, 0.0, 0.0)
	glRotatef(180, 0.0, 1.0, 0.0)
	glTranslatef(0.0, view_distance, 0)

	#position the satelite directly above the desired latitude and longitude
	glRotatef(latitude, 1.0, 0.0, 0.0)
	glRotatef(longitude, 0.0, 0.0, -1.0)
	glCallList(1)
	glPopMatrix()
	

	
	glPopMatrix()

	# Draw the skybox
	glDepthMask(False)
	

	#glTranslatef(0.0, 5, 0)
	glCallList(2)
	#draw target

	
	# Re-enable lighting and depth test before we redraw the world
	glEnable(GL_LIGHTING)
	glDepthMask(True)		
	
	# Here is where we would draw the rest of the world in a game


	pygame.display.flip()
def get_input():
	global view_distance, view_angle,longitude_offset
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
	#if keystate[K_UP] and view_angle[0] < 90: view_angle[0] += 1.0
	#if keystate[K_DOWN] and view_angle[0] > -90: view_angle[0] -= 1.0

def main():
	curtime=time()
	while True:
		get_input()
		draw()
		#sleep(.25)
		lasttime=curtime
		curtime=time()
		print "fps: "+str(1.0/(curtime-lasttime))
if __name__ == "__main__": main()
