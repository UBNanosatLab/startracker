# -*- coding: utf-8 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
import socket
from datetime import datetime
from pygame.locals import *
import sys, os
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

view_distance = 6*6781000/6367444.7 #5*orbit height/ earth radius
view_angle = [0.0, 0.0]

latitude = 42.886448
longitude = -78.878372

    
def draw():
    #RESET ALL----------------------------------------
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port)) 
    data = s.recv(size).split()
    s.close()
    ra=float(data[9].split(",")[0])
    dec=float(data[9].split(",")[1])
    latitude=float(data[0].split(",")[0])
    longitude=float(data[0].split(",")[1])
    altitude=float(data[0].split(",")[2])
    if altitude < 0.0:
        altitude=-altitude
        latitude=-latitude
        longitude=(longitude+360)%360-180
    
    utc = datetime.fromtimestamp(float(data[8]))
    gst = sidereal.SiderealTime.fromDatetime ( utc )
    lst = gst.lst(longitude)
    ra_earth  = sidereal.hoursToRadians(lst.hours%24.0)
    dec_earth = latitude
    #print data
    view_distance = 6*altitude/6367444.7 #5*orbit height/ earth radius
    
    glLoadIdentity()
    glDisable(GL_LIGHTING)



    #DRAW EARTH---------------------------------------

    glRotatef(view_angle[0], -1.0, 0.0, 0.0)
    glRotatef(view_angle[1], 0.0, 1.0, 0.0)

    #point the camera at the target ra and dec
    glRotatef(dec, -1.0, 0.0, 0.0)
    glRotatef(ra, 0.0, 1.0, 0.0)

    #map calculated sky ra and dec to the given latitude and longitude on earth
    glPushMatrix()
    glRotatef(dec_earth, 1.0, 0.0, 0.0)
    glRotatef(ra_earth, 0.0, -1.0, 0.0)
    
    glPushMatrix()
    glRotatef(90, 1.0, 0.0, 0.0)
    glRotatef(180, 0.0, 1.0, 0.0)
    glTranslatef(0.0, view_distance, 0)

    #position the satelite directly above the desired latitude and longitude
    glRotatef(latitude, 1.0, 0.0, 0.0)
    glRotatef(longitude, 0.0, 0.0, -1.0)
    #glRotatef(42.886448, 1.0, 0.0, 0.0)
    #glRotatef(-78.878372, 0.0, 0.0, -1.0)
    glCallList(1)
    glPopMatrix()
    glPopMatrix()

    glDepthMask(False)
    
    # Draw the skybox
    glCallList(2)
    
    # Re-enable lighting and depth test before we redraw the world
    glEnable(GL_LIGHTING)
    glDepthMask(True)        
    
    # Here is where we would draw the rest of the world in a game


    pygame.display.flip()
def get_input():
    global view_distance, view_angle, latitude, longitude
    keystate = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keystate[K_ESCAPE]:
            pygame.quit(); sys.exit()
    if keystate[K_PAGEUP]:
        longitude -= 0.5
    if keystate[K_PAGEDOWN]:
        longitude += 0.5
    if keystate[K_RIGHT]: view_angle[1] += 1.0
    if keystate[K_LEFT]: view_angle[1] -= 1.0
    if keystate[K_UP] and view_angle[0] < 90: view_angle[0] += 1.0
    if keystate[K_DOWN] and view_angle[0] > -90: view_angle[0] -= 1.0

def main():
    while True:
        get_input()
        draw()
if __name__ == "__main__": main()
