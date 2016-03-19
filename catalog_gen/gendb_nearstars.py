import csv
import math
def nearestStars(inputText, outputText):
    outFile = open(outputText, "w")
    with open(inputText) as csvfile:
        reader = csv.reader(csvfile)
        cat = list(reader)
    count = 0
    foundErrorValue = 0
    foundValuesList = []
    foundDistanceList = []
    for item in cat:
        first = 9998
        second = 9998
        third = 9998
        firstValue = 0
        secondValue = 1
        thirdValue = 2
        if(count%100 == 0):
            print(str(count) + "/" +str(len(cat)) + " | {0:.2f}".format(count/len(cat) *100) + " %")
        count = count+1
        for item2 in cat:
            ra1 = float(item[2])
            ra2 = float(item2[2])
            dec1 = float(item[3])
            dec2 = float(item2[3])
            dis = math.fabs(distance(ra1, dec1, ra2, dec2))
            if(dis<=first):
                tempValue = firstValue
                firstValue = item2[0]
                thirdValue = secondValue
                secondValue = tempValue

                temp = first
                first = dis
                third = second
                second = temp
            elif(dis<=second):
                thirdValue = secondValue
                secondValue = item2[0]

                third = second
                second = dis
            elif(dis<=third):
                third = dis
                thirdValue = item2[0]

        foundDistanceList = [first, second, third]
        foundValuesList = [firstValue, secondValue, thirdValue]
        for item2 in cat:
            ra1 = float(item[2])
            ra2 = float(item2[2])
            dec1 = float(item[3])
            dec2 = float(item2[3])
            dis = math.fabs(distance(ra1, dec1, ra2, dec2))

            if item2[0] in foundValuesList:
                x = 5
            else:
                if dis <=float(foundDistanceList[2]) + 1/64:
                    foundErrorValue = foundErrorValue + 1
                    print("Found Error Value: " + str(foundErrorValue))
                    foundValuesList.append(item2[0])
        line = item[0] + "," + item[1] + "," + item[2] + "," + item[3] + ","
        for id in foundValuesList:
            line = line + id + ","
        line = line[:-1]
        line = line + "\n"
        line = line.replace(" ", "")
        outFile.write(line)
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