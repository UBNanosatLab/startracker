calibrate.sh
new dependancies:
- astrometry.net
input:
- an image of the stars taken with the startracker camera
output:
- star position error in arcseconds
- image size in pixels (x and y)
- field of view size in degrees (x and y)
- pixel size in arcseconds per pixel
- save this information to calibration/calibration.txt

gendb_brightness.py
input:
- constelation database where stars are arranges by distance from the first star
- maximum acceptable error in star magnitude
outputs:
- a constellation database where stars are arranged by brightness

nearstars2db.sh:
input:
- the output of calibrate.sh
outputs:
- constelationdb.dat: a constelation database in which stars are sorted by brightness

gendb_info.py
input:
- the output of nearstars2db.sh
outputs:
- the distance between all stars in a constelation database in arcseconds

calculate_db_size.sh - calculates the
input:
- the output of gendb_info.py
outputs:
- optimal binsize for each of the three parameters used to lookup constelations in the database
- final size of the databasse
- save this information to calibration/dbsize.txt

db_stats.sh
input:
- calibration/calibration.txt
- calibration/dbsize.txt
- the output of gendb_info.py
outputs:
- 3 csv files containing the distribution of raw star lookup parameters - data[1-3].csv
- 3 csv files containing the distribution of wrapped star lookup parameters - data[4-6].csv

