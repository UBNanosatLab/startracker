"""
    vspace.py

    Visual Python Space Demo
    by Ronald Adam 3/20/2005

    A fun little Visual Python Demo
    Free to use anyway you want, but please send
    me any changes if you make any improvements.
 
    Email: ron@ronadam.com

"""
from __future__ import division
from visual import *
import random


if __name__ == '__main__':

    # Set up window and sceen.
    scene = display()
    scene.fullscreen = 0
    scene.autocenter = 0
    scene.autoscale = 0
    scene.userzoom = 0
    scene.userspin = 0
    scene.ambient = 0
    scene.range = (10,10,10)
    scene.scale = (.1,.1,.1)
    minmag=10

    # Size of the visible universe.
    spacesize = 500

    # Fill outerspace with stars.
    radius = 1
    outerspace = frame()
    starfile = open("catalog.dat")


    for line in starfile.readlines():
        temp=line.rstrip().split(",")
        pos=[spacesize*1.5*math.cos(math.radians(float(temp[2])))*math.cos(math.radians(float(temp[3]))),spacesize*1.5*math.sin(math.radians(float(temp[2])))*math.cos(math.radians(float(temp[3]))),spacesize*1.5*math.sin(math.radians(float(temp[3])))]
        mag=math.pow(100,(minmag-float(temp[1]))/5-1)
        print pos
        print 
        points(frame=outerspace, pos=pos, size=2, color=[mag,mag,mag])
    starfile.close()

 
    # Spaceship view would go here if we had one.
    xr = yr = zr = yv = xv = zv = 0

    # Main loop
    while True:
        # Adjust mouse response in case of zoom.
        rotspeed = 5000 #+mag(scene.mouse.camera-scene.center)

        # The control stick.
        rx, ry, rz = scene.mouse.pos
        yv += (ry-yv)/10
        try:
            if scene.mouse.button == 'left':
                zv += (rx-zv)/5
        except:
            xv += (rx-xv)/10

        # rotate star frame
        outerspace.rotate( angle=xv/rotspeed, axis=[0,6,0], origin=scene.center)
        outerspace.rotate( angle=yv/rotspeed, axis=[-6,0,0], origin=scene.center)
        outerspace.rotate( angle=zv/rotspeed, axis=[0,0,8], origin=scene.center)
        rate(20)




