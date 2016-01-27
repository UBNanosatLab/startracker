#!/usr/bin/python

# Written by Jeff Albro jeff@jeffalbro.net
# Released under the GPL

#Required: Python 2.2 or later, Python Imaging Library

##############################
# These variables set the mapping range
# You must use decimal notation

lowra=0.0
highra=24

lowdec=-40.0
highdec=40.0

#how faint?
maglimit=5.4

#pixels per degree
ppd=5.0

##########################
# change to float values, and change ra from hours to degrees
def normalize(starlist):
	for index in range(len(starlist)):
		starlist[index][0]=(24.0/360.0)*float(starlist[index][0])
		starlist[index][1]=float(starlist[index][1])
		starlist[index][2]=float(starlist[index][2])
	return starlist

##########################
def crop(starlist, lowra, highra, lowdec, highdec, maglimit):

	newlist=[[0,0,0]]

	for star in starlist:
		
		starra=star[0]
		stardec=star[1]
		starmag=star[2]

		if lowra < starra < highra:
			if lowdec < stardec < highdec:
				if starmag < maglimit:
					newlist.append([ starra, stardec, starmag])

	#Nix the first fake entry 
	newlist.pop(0)

	return newlist

##########################
def remap(starlist, lowra, highra, lowdec, highdec, maglimit):

	# returns field with units in degrees, and changes 0,0 to upper left
	# also remaps magnitude.  This part could require some tuning.
	newlist=[[0,0,0]]

	#print "Doing remap"
	#print

	baseliney=(highdec-90)*-1.0

	for star in starlist:
		
		starra=star[0]
		stardec=star[1]
		starmag=star[2]


		#print "original ra, dec, mag:"
		#print starra, stardec, starmag

		newx=(highra-starra)*(360.0/24.0)

		adjustedy=(stardec-90.0)*-1.0
		newy=adjustedy-baseliney
	
		#anything less than 0, (sirius at -1.5) gets mapped to 0
		if starmag < 0:
			starmag=0

		#magnitude gets remaped from 8 to 0, 8 being the brightest
		newz=8.0-starmag

		#print "new ra, dec, mag:"
		#print newx, newy, newz
		#print
		
		newlist.append([ newx, newy, newz])

	#Nix the first fake entry 
	newlist.pop(0)

	#print "Number of stars: ", len(newlist)

	return newlist

##########################
def fieldsize(lowra, highra, lowdec, highdec):

	#Returns field size in degrees x and degrees y
	degx=(highra-lowra)*(360/24)
	degy=highdec-lowdec

	return degx, degy


##########################
def imagelist(starlist, degx, degy, ppd):

	sizex=int(math.ceil(ppd*degx)+4)
	sizey=int(math.ceil(ppd*degy)+4)
	im=Image.new("L", (sizex,sizey))

	#print "size degrees"
	#print degx, degy

	#print "size pixels"
	#print sizex, sizey

	#print "size from image"
	#print im.size

	for star in starlist:

		starx=star[0]
		stary=star[1]
		starz=star[2]


		#print "original star x, y, z:"
		#print starx, stary, starz

		pixelx=int(math.floor(starx*ppd)+2)
		pixely=int(math.floor(stary*ppd)+2)
		# 8*8=64, 64*4=256, 256-1=255, the brightest
		brightness=int(round((starz*starz*4)-1))

		#breadcrumb action...
		#print "values:"
		#print pixelx, pixely, brightness

		#print im.getpixel((pixelx, pixely))
		
		im.putpixel((pixelx, pixely), brightness)
		im.putpixel((pixelx-1, pixely), brightness)
		im.putpixel((pixelx, pixely-1), brightness)
		im.putpixel((pixelx+1, pixely), brightness)
		im.putpixel((pixelx, pixely+1), brightness)

	im.save("starmap.png", "PNG")

##########################
# Used in creating an AutoCAD output... not currently used
def plotstar(starx, stary, brightness):

	#print "_color"
	#print "25"+str(int(round(8-brightness)))

	print "_text"
	print str(starx)+","+str(stary)
	print ".1"  # text size
	print "0"  # rotation
	print int(round(8-brightness))

#########################
import Image
import ImageDraw
import math

##########################
# load the star database

starfile = open("stars.db")

starlist=[[0,0,0]]

for line in starfile.readlines():
    starlist.append(line.rstrip().split(","))

starfile.close()

#Nix the first fake entry 
starlist.pop(0)

starlist=normalize(starlist)

croplist=crop(starlist, lowra, highra, lowdec, highdec, maglimit)

maplist=remap(croplist, lowra, highra, lowdec, highdec, maglimit)

degx,degy=fieldsize(lowra, highra, lowdec, highdec)

imagelist(maplist, degx, degy, ppd)


