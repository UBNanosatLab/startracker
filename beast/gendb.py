#!/usr/bin/python
from math import *
import sys

maxdist=float(sys.argv[1])

mag=[]
ra=[]
dec=[]
length=0

starfile = open("cat.txt")
for line in starfile.readlines():
    star=line.rstrip().split(" ")
    mag.append(float(star[0]))
    ra.append(float(star[1]))
    dec.append(float(star[2]))
    length +=1
starfile.close()

for i in range(0,length):
    for j in range(i+1,length):
        xdot=cos(radians(ra[i]))*cos(radians(dec[i]))*cos(radians(ra[j]))*cos(radians(dec[j]))
        ydot=sin(radians(ra[i]))*cos(radians(dec[i]))*sin(radians(ra[j]))*cos(radians(dec[j]))
        zdot=sin(radians(dec[i]))*sin(radians(dec[j]))
        dist=degrees(acos(xdot+ydot+zdot))
        if dist<maxdist:
            print dist,i,j
