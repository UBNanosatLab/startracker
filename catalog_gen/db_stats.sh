#!/bin/sh
source calibration/calibration.txt
source calibration/dbsize.txt

cut -d ',' -f 1 < info.txt | sed s:$:/$ARC_ERR:g|bc| sort -n | uniq -c| awk 'OFS="," {print $2,$1}'>data1.csv
cut -d ',' -f 2 < info.txt | sed s:$:/$ARC_ERR:g|bc| sort -n | uniq -c| awk 'OFS="," {print $2,$1}'>data2.csv
cut -d ',' -f 3 < info.txt | sed s:$:/$ARC_ERR:g|bc| sort -n | uniq -c| awk 'OFS="," {print $2,$1}'>data3.csv

cut -d ',' -f 1 < info.txt | sed s:$:%\($ARC_ERR*$PARAM1\)/$ARC_ERR:g|bc| sort -n | uniq -c| awk 'OFS="," {print $2,$1}'>data4.csv
cut -d ',' -f 2 < info.txt | sed s:$:%\($ARC_ERR*$PARAM2\)/$ARC_ERR:g|bc| sort -n | uniq -c| awk 'OFS="," {print $2,$1}'>data5.csv
cut -d ',' -f 3 < info.txt | sed s:$:%\($ARC_ERR*$PARAM3\)/$ARC_ERR:g|bc| sort -n | uniq -c| awk 'OFS="," {print $2,$1}'>data6.csv