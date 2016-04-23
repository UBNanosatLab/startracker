import csv

#Takes in hip_main.dat and writes to a file with stars less than 8 magnitude
#Sample fileout looks like: Star ID, Brightness, RA, DEC

def magnitudeSort(inputText, outputText):
    outFile = open(outputText, "w")

    with open(inputText) as csvfile:
        reader = csv.reader(csvfile, delimiter='|')
        for line in reader:
            if line[5].strip(" ") == "":
                x=5
            elif float(line[5].strip()) <=8:
                if(line[8].strip(" ") == ""):
                    print("ERRROR at line " + line[8])
                else:
                    newRow = line[8].strip("0")
                    if(newRow[0] == "."):
                        newRow = "0" + newRow
                    print(newRow)
                    float(newRow)
                    newLine = line[1] + "," + line[5] + "," + newRow + "," + line[9].replace("+", "") + "\n"
                    outFile.write(newLine)

inputFile = "hip_main.dat"
outputFile = "catalog.dat"

magnitudeSort(inputFile, outputFile)