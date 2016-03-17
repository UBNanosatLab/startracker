#!/usr/bin/python
import math

import sys
stardb={}
starfile = open("catalog.dat")
for line in starfile.readlines():
    star=line.rstrip(' \t').split(",")
    stardb[int(star[0])]=[float(star[1]),float(star[2]),float(star[3])]

