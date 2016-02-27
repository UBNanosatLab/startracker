import os, sys
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame, pygame.image
from pygame.locals import *

pygame.init()

textures = [0]

def resize((width, height)):
    if height==0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.5, 10000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():
    glEnable(GL_TEXTURE_2D)

    glEnable(GL_BLEND)#masking functions
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    #glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable( GL_ALPHA_TEST )
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

#(set screen resolution)
screenx = 1
screeny = 1
video_flags = OPENGL|DOUBLEBUF
surface = pygame.display.set_mode((screenx,screeny), video_flags)
resize((screenx,screeny))
init()

def main():
    EarthFile = os.path.join('Data', 'earth.jpg')
    EarthSurface = pygame.image.load(EarthFile)
##    EarthSurface.set_colorkey((255,255,255),0)
    EarthData = pygame.image.tostring(EarthSurface, "RGBA", 1)

    LatLongFile = os.path.join('Data', 'LatLong.jpg')
    LatLongSurface = pygame.image.load(LatLongFile)
##    LatLongSurface.set_colorkey((255,255,255),0)
    LatLongData = pygame.image.tostring(LatLongSurface, "RGBA", 1)

    SpikeFile = os.path.join('Data', 'Spike.png')
    SpikeSurface = pygame.image.load(SpikeFile)
##    SpikeSurface.set_colorkey((255,255,255),0)
    SpikeData = pygame.image.tostring(SpikeSurface, "RGBA", 1)

    SpikeBaseFile = os.path.join('Data', 'SpikeBase.jpg')
    SpikeBaseSurface = pygame.image.load(SpikeBaseFile)
##    SpikeBaseSurface.set_colorkey((255,255,255),0)
    SpikeBaseData = pygame.image.tostring(SpikeBaseSurface, "RGBA", 1)

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

    glGenLists(1)
    glNewList(2, GL_COMPILE)#LatLong
    glBindTexture(GL_TEXTURE_2D, textures[0])
    glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, LatLongSurface.get_width(), LatLongSurface.get_height(), 0,
                  GL_RGBA, GL_UNSIGNED_BYTE, LatLongData )
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    Sphere = gluNewQuadric()
    gluQuadricTexture(Sphere, GL_TRUE)
    gluSphere(Sphere, 5.1, 24, 10)
    glEndList()

    glGenLists(1)
    glNewList(3, GL_COMPILE)#Spike of Density
    size = 0.05
    glBindTexture(GL_TEXTURE_2D, textures[0])
    glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, SpikeSurface.get_width(), SpikeSurface.get_height(), 0,
                  GL_RGBA, GL_UNSIGNED_BYTE, SpikeData )
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f( -1.0*size,  0.0*size, 0.0*size)
    glTexCoord2f(1.0, 0.0); glVertex3f(  1.0*size,  0.0*size, 0.0*size)
    glTexCoord2f(1.0, 1.0); glVertex3f(  1.0*size, -66.0*size, 0.0*size)
    glTexCoord2f(0.0, 1.0); glVertex3f( -1.0*size, -66.0*size, 0.0*size)

    glTexCoord2f(0.0, 0.0); glVertex3f( 0.0*size,  0.0*size, -1.0*size)
    glTexCoord2f(1.0, 0.0); glVertex3f( 0.0*size,  0.0*size, 1.0*size)
    glTexCoord2f(1.0, 1.0); glVertex3f( 0.0*size, -66.0*size, 1.0*size)
    glTexCoord2f(0.0, 1.0); glVertex3f( 0.0*size, -66.0*size, -1.0*size)
    glEnd();
    glBindTexture(GL_TEXTURE_2D, textures[0])
    glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, SpikeBaseSurface.get_width(), SpikeBaseSurface.get_height(), 0,
                  GL_RGBA, GL_UNSIGNED_BYTE, SpikeBaseData )
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f( -1.0*size, 0.0*size, -1.0*size)
    glTexCoord2f(1.0, 0.0); glVertex3f(  1.0*size, 0.0*size, -1.0*size)
    glTexCoord2f(1.0, 1.0); glVertex3f(  1.0*size, 0.0*size,  1.0*size)
    glTexCoord2f(0.0, 1.0); glVertex3f( -1.0*size, 0.0*size,  1.0*size)
    glEnd();
    glEndList()





