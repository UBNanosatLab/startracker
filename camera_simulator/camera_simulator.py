# -*- coding: utf-8 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
import socket
from datetime import datetime
from time import time, sleep
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
size = 1024 

#view_distance = 5*6781000/6367444.7 #5*orbit height/ earth radius
view_distance = 6
view_angle = [0.0, 0.0,0.0]
longitude_offset=0.0
	
def draw():
	latitude = 42.886448
	longitude = -78.878372 
	latitude = 30
	longitude = 0
	#RESET ALL----------------------------------------
	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port)) 
	data = s.recv(size).split()
	s.close()

	body2ECI=np.array(data[5].split(",")).astype(np.float).reshape((3, 3))
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
	print data
	#latitude=float(data[0].split(",")[0])
	#longitude=float(data[0].split(",")[1])
	altitude=float(data[0].split(",")[2])
	if altitude < 0.0:
		altitude=-altitude
		latitude=-latitude
		longitude=(longitude+360)%360-180
	ts=float(data[0].split(",")[3])
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
	print ts
	glLoadIdentity()
	glDisable(GL_LIGHTING)



	#DRAW EARTH---------------------------------------

	#point the camera at the target ra and dec
	glRotatef(DEC, -1.0, 0.0, 0.0)
	glRotatef(RA, 0.0, -1.0, 0.0)
	x=np.cos(np.radians(RA))*np.cos(np.radians(DEC))
	y=np.sin(np.radians(RA))*np.cos(np.radians(DEC))
	z=np.sin(np.radians(DEC))
	
	glRotatef(ORIENTATION+180, -y, z, -x)


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
	
	glRotatef(-90, 1.0, 0.0, 0.0)
	glTranslatef(0, view_distance, 0)
	glRotatef(ts%360, 0,0,1)
	
	glCallList(3)
	glPopMatrix()

	glDepthMask(False)
	
	# Draw the skybox
	glCallList(2)
	#glTranslatef(0.0, 5, 0)
	#glCallList(3)
	
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
		#sleep(1)
		lasttime=curtime
		curtime=time()
		print "fps: "+str(1.0/(curtime-lasttime))
if __name__ == "__main__": main()
