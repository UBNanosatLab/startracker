import csv
import math
#Takes in a catalog of stars with ID, Right Ascension and Declination
#Outputs catalog with three closest(or more if within 1/64 of degree of distance of third closest star) stars appended to each star entry
#Sample output Looks like: ID, RA, DEC, closestStarId1, closestStarId2, closestStarId3(and more if within error)
def nearestStars(inputText, outputText):
    outFile = open(outputText, "w")
    with open(inputText) as csvfile:
        reader = csv.reader(csvfile)
        cat = list(reader)
    count = 0
    #Goes through every star in Catalog
    for star in cat:

        #Initializing variables.  Made distances 9998 as default value
        closestStarDistance = 9998
        secondClosestStarDistance = 9998
        thirdClosestDistance = 9998

        closestStarID = 0
        secondClosestStarID = 0
        thirdClosestStarID = 0

        #Prints progress of sort
        if(count%100 == 0):
            print(str(count) + "/" +str(len(cat)) + " | {0:.2f}".format(count/len(cat) *100) + " %")
        count = count+1

        for starCandidate in cat:
            #Finds distance between star and the star candidate (star[2] refers to right ascension, star[3] refers to declination)
            ra1 = float(star[2])
            ra2 = float(starCandidate[2])
            dec1 = float(star[3])
            dec2 = float(starCandidate[3])
            dis = math.fabs(distance(ra1, dec1, ra2, dec2))

            #If Star candiate distance is closest found
            if(dis<=closestStarDistance):
                tempValue = closestStarID
                closestStarID = starCandidate[0]
                thirdClosestStarID = secondClosestStarID
                secondClosestStarID = tempValue

                temp = closestStarDistance
                closestStarDistance = dis
                thirdClosestDistance = secondClosestStarDistance
                secondClosestStarDistance = temp
            #If star candiate is second closest found
            elif(dis<=secondClosestStarDistance):
                thirdClosestStarID = secondClosestStarID
                secondClosestStarID = starCandidate[0]

                thirdClosestDistance = secondClosestStarDistance
                secondClosestStarDistance = dis
            #If star candidate is third closest found
            elif(dis<=thirdClosestDistance):
                thirdClosestDistance = dis
                thirdClosestStarID = starCandidate[0]

        #At this point, we have looked through every candidate and found the three closest stars and their corresponding ID's
        closestDistanceList = [closestStarDistance, secondClosestStarDistance, thirdClosestDistance]
        closestIDList = [closestStarID, secondClosestStarID, thirdClosestStarID]

        #Looks through every star in catologue and determines if it is within 1/64 + degress of third farthest star
        #If it is, it is appended to the closestIDList
        for starCandidate in cat:
            ra1 = float(star[2])
            ra2 = float(starCandidate[2])
            dec1 = float(star[3])
            dec2 = float(starCandidate[3])
            dis = math.fabs(distance(ra1, dec1, ra2, dec2))
        #If StarCandidate ID is in closetIDList, means its a duplicate and should be skipped
            if starCandidate[0] in closestIDList:
                break;
            else:
                if dis <=float(closestDistanceList[2]) + 1/64:
                    closestIDList.append(starCandidate[0])
        line = star[0] + "," + star[1] + "," + star[2] + "," + star[3] + ","

        #Once we have found stars within error, make a line seperated by commas of these stars and add them to the outputfile
        for id in closestIDList:
            line = line + id + ","
        line = line[:-1]
        line = line + "\n"
        line = line.replace(" ", "")
        outFile.write(line)

#Determines the distance between two stars given right ascension and declination
def distance(ra1,dec1,ra2,dec2):
    if(ra1 == ra2 and dec1 == dec2):
        return 9999
    else:
        x1=math.cos(math.radians(ra1))*math.cos(math.radians(dec1))
        y1=math.sin(math.radians(ra1))*math.cos(math.radians(dec1))
        z1=math.sin(math.radians(dec1))
        x2=math.cos(math.radians(ra2))*math.cos(math.radians(dec2))
        y2=math.sin(math.radians(ra2))*math.cos(math.radians(dec2))
        z2=math.sin(math.radians(dec2))
        return math.degrees(math.acos(x1*x2+y1*y2+z1*z2))

inputFile = "catalogRemoved.dat"
outputFile = "nearStars.dat"

nearestStars(inputFile, outputFile)