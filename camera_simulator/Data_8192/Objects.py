import os, sys
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame, pygame.image
from pygame.locals import *

pygame.init()

textures = [0]

def resize((width, height)):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(9, float(width)/height, .1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():
    glEnable(GL_BLEND)#masking functions
    ##glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    #glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    ##glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glShadeModel(GL_SMOOTH)
    ##glEnable( GL_ALPHA_TEST )
    ##glDepthFunc(GL_LEQUAL)
    ##glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

#(set screen resolution)
screenx = 720
screeny = 720
surface = pygame.display.set_mode((screenx,screeny), OPENGL|DOUBLEBUF|NOFRAME)
#surface = pygame.display.set_mode((screenx,screeny), OPENGL|DOUBLEBUF)
resize((screenx,screeny))
init()

def main():
    EarthFile = os.path.join('Data', 'earth.jpg')
    EarthSurface = pygame.image.load(EarthFile)
    EarthData = pygame.image.tostring(EarthSurface, "RGBA", 1)

    glGenLists(1)
    glNewList(1, GL_COMPILE)#Self
    glBindTexture(GL_TEXTURE_2D, textures[0])
    glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, EarthSurface.get_width(), EarthSurface.get_height(), 0,
                  GL_RGBA, GL_UNSIGNED_BYTE, EarthData )
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    Sphere = gluNewQuadric()
    gluQuadricTexture(Sphere, GL_TRUE)
    gluSphere(Sphere, 5.0, 80, 80)
    glEndList()
    
    #render skybox
    glGenLists(1)
    glNewList(2, GL_COMPILE)    
    glScale(1, -1, 1)
    glEnable(GL_TEXTURE_CUBE_MAP)
    files = ['ft.png','bk.png','dn.png','up.png','rt.png','lt.png']
    faces = [GL_TEXTURE_CUBE_MAP_POSITIVE_X,
    GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
    GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
    GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
    GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
    GL_TEXTURE_CUBE_MAP_NEGATIVE_Z]
    glClearColor(0.3,0.3,0.3,1.0)
    glEnable(GL_DEPTH_TEST)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, glGenTextures(1))
    
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    
    for i in range(6) :
        texture_surface = pygame.image.load(os.path.join('Data', files[i]))
        width, height = texture_surface.get_rect().size
        img = pygame.image.tostring(texture_surface, 'RGB', True)
        glTexImage2D(faces[i], 0, GL_LUMINANCE, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    
    m=100
    planes = (
        ([-m, -m, -m],[ m, -m, -m],[ m, m, -m],[-m, m, -m]),#front
        ([-m, -m, m],[-m, m, m],[ m, m, m],[ m, -m, m]),# back
        ([ m, -m, -m],[ m, -m, m],[ m, m, m],[ m, m, -m]),# right
        ([-m, -m, -m],[-m, m, -m],[-m, m, m],[-m, -m, m]),# left
        ([-m, -m, -m],[-m, -m, m],[ m, -m, m],[ m, -m, -m]),# down
        ([-m, m, -m],[ m, m, -m],[ m, m, m],[-m, m, m]))# up
    for plane in planes:
        glBegin(GL_QUADS)
        for vertex in plane:
            glTexCoord3fv(vertex)
            glVertex3fv(vertex)
        glEnd()
    glDisable(GL_TEXTURE_CUBE_MAP)
    glScale(1, 1, 1)
    glEndList()
