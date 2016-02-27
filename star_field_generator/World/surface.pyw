from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
import sys, os
from pygame.locals import *
def main(screendimfull):
    screenx = screendimfull[0]
    screeny = screendimfull[1]
    FullscreenWindowed = screendimfull[2]
    if FullscreenWindowed == 1:
        video_flags = OPENGL|DOUBLEBUF|FULLSCREEN
    elif FullscreenWindowed == 2:
        video_flags = OPENGL|DOUBLEBUF
    surface = pygame.display.set_mode((screenx,screeny), video_flags)
    return surface
