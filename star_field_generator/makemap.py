#!/usr/bin/python
import Image
import ImageDraw
import math
import sys

def mag2val(mag,refmag,refval):
	magconst=refmag+2.5*math.log10(refval)
	val=10**((mag-magconst)/-2.5)
	if val > 255:
		val=255
	return val

imagex=1024*int(sys.argv[1])*4
imagey=1024*int(sys.argv[1])*2

im=Image.new("L", (imagex,imagey))
starfile = open("catalog.dat")
for line in starfile.readlines():
    star=line.rstrip().split(",")
    ra=float(star[2])
    dec=float(star[3])
    mag=float(star[1])
    
    #this formula was experementally derived from Tennenbaum's laptop screen.
    #minmag was then adjusted until a 7.5 magnitude star has a brightness of 20
   
    brightness=mag2val(mag,6.5,20)
    
    pixelx=(360.0-ra)*imagex/360
    pixely=(90.0-dec)*imagey/180
    distortion=1/math.cos(math.radians(dec))

    for x in range(int(round(pixelx-distortion/2)), int(round(pixelx+distortion/2))):
        im.putpixel(((-x)%imagex, int(round(pixely))),brightness)

im.save("starmap.png", "PNG")
starfile.close()
