# -*- coding: utf-8 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import sys, os
if sys.platform == 'win32' or sys.platform == 'win64':
    os.environ['SDL_VIDEO_CENTERED'] = '1'
dir='Data'
sys.path.append(dir)
import GL, Objects, surface

pygame.init()

screendimfull = [800,640,2]
surface = surface.main(screendimfull)
pygame.display.set_caption('ICC World - Ian Mallett 2007') #(set program name)
Objects.main()
GL.resize((screendimfull[0], screendimfull[1]))#Resize OpenGL Window
GL.init()#Init OpenGL

view_distance = 18.0
view_angle = [0.0, 0.0]

def draw():
    #RESET ALL----------------------------------------
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    #BASIC CAMERA VIEW--------------------------------
    glTranslatef(0.0, 0.0, -view_distance)
    glRotatef(-90, 1.0, 0.0, 0.0)
    glRotatef(view_angle[0], 1.0, 0.0, 0.0)
    glRotatef(view_angle[1], 0.0, 0.0, 1.0)
    #DRAW EARTH---------------------------------------
    glCallList(1)
##    #   DRAW LAT/LONG LINES---------------------------
##    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
##    glCallList(2)
##    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
##    #   DRAW SPIKES OF DENSITY------------------------
##    if   point_data[2] == "W":  glRotatef(-point_data[0], 0.0, 0.0, 1.0)
##    elif point_data[2] == "E":  glRotatef( point_data[0], 0.0, 0.0, 1.0)
##    if   point_data[3] == "N":  glRotatef(-point_data[1], 1.0, 0.0, 0.0)
##    elif point_data[3] == "S":  glRotatef( point_data[1], 1.0, 0.0, 0.0)
    glCallList(4)
    #FLIP TO SCREEN-----------------------------------
    pygame.display.flip()
def get_input():
    global view_distance, view_angle
    keystate = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keystate[K_ESCAPE]:
            pygame.quit(); sys.exit()
    if keystate[K_PAGEUP] and view_distance < 18.0:
        view_distance += 0.06
    if keystate[K_PAGEDOWN] and view_distance > 5.55:
        view_distance -= 0.06
    if keystate[K_END]: view_distance = 18.0
    if keystate[K_KP4]: view_angle[1] += 1.0*((view_distance-5.0)/13.0)
    if keystate[K_KP6]: view_angle[1] -= 1.0*((view_distance-5.0)/13.0)
    if keystate[K_KP8] and view_angle[0] < 90: view_angle[0] += 1.0*((view_distance-5.0)/13.0)
    if keystate[K_KP2] and view_angle[0] > -90: view_angle[0] -= 1.0*((view_distance-5.0)/13.0)
def build_list_of_points():
    f_read = open('PointList.txt', 'r')
    point_data = f_read.readlines()
##    Data format is (000.000000W, 000.000000N)
    glGenLists(1)
    glNewList(4, GL_COMPILE)
    for point in point_data:
        p = str(point)
        EastWestCoord   = float(p[1] +p[2] +p[3] +p[4] +p[5] +p[6] +p[7] +p[8] +p[9] +p[10])
        NorthSouthCoord = float(p[14]+p[15]+p[16]+p[17]+p[18]+p[19]+p[20]+p[21]+p[22]+p[23])
        glPushMatrix()
        if   p[11] == "W":  glRotatef(-EastWestCoord, 0.0, 0.0, 1.0)
        else:               glRotatef( EastWestCoord, 0.0, 0.0, 1.0)
        if   p[24] == "N":  glRotatef(-NorthSouthCoord, 1.0, 0.0, 0.0)
        else:               glRotatef( NorthSouthCoord, 1.0, 0.0, 0.0)
        glTranslatef(0.0, -5.0, 0.0)
        glScalef(0.1,1.0,0.1)
        glCallList(3)
        glPopMatrix()
    glEndList()
def main():
    build_list_of_points()
    while True:
        get_input()
        draw()
if __name__ == "__main__": main()










        
