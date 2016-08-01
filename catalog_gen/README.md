#Workflow:
1. Edit MIN_MAG & NOISE_MAG in calibrate.sh
2. Run ./calibrate.sh samplefield.png
3. Run ./hip2cat.sh
4. Run ./cat2db.sh
5. Run ./db2beast.sh


#Scripts:

###calibrate.sh

#####dependancies:
- astrometry.net

#####input:
- an image of the stars taken with the startracker camera

#####output:
- star position error in arcseconds
- image size in pixels (x and y)
- field of view size in degrees (x and y)
- pixel size in arcseconds per pixel
- save this information to calibration/calibration.txt

###gendb_brightness.py
#####input:
- constelation database where stars are arranged by distance from the first star
- maximum acceptable error in star magnitude

#####output:
- a constellation database where stars are arranged by brightness

###nearstars2db.sh
#####input:
- the output of calibrate.sh

#####output:
- constelationdb.dat: a constelation database in which stars are sorted by brightness

###gendb_info.py
#####input:
- nearStars.dat
- output of nearstars2db.sh

#####output:
- the distance between all stars in a constellation database in arcseconds

###calculate_db_size.sh
#####input:
- the output of gendb_info.py

#####output:
- optimal binsize for each of the three parameters used to lookup constelations in the database
- final size of the databasse
- save this information to calibrate/dbsize.txt

###db_stats.sh
#####input:
- calibrate/calibration.txt  (from calibrate.sh)
- info/dbsize.txt (from db_size.sh)
- info/starline.txt (from db_size.sh)

#####output:
- 3 csv files containing the distribution of raw star lookup parameters - info/param[1-3].csv
- 3 csv files containing the distribution of wrapped star lookup parameters - info/param[1-3]_wrapped.csv

To compile beastgen, you need to do sudo apt-get install g++-multilib 
