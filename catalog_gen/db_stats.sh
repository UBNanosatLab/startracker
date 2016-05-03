#!/bin/sh
source calibration/calibration.txt
source calibration/dbsize.txt

cd info
cut -d ',' -f 1 < starline.txt | sed s:$:/$ARC_ERR:g|bc| sort -n | uniq -c| awk 'OFS="," {print $2,$1}'>param1.csv
cut -d ',' -f 2 < starline.txt | sed s:$:/$ARC_ERR:g|bc| sort -n | uniq -c| awk 'OFS="," {print $2,$1}'>param2.csv
cut -d ',' -f 3 < starline.txt | sed s:$:/$ARC_ERR:g|bc| sort -n | uniq -c| awk 'OFS="," {print $2,$1}'>param3.csv

cut -d ',' -f 1 < starline.txt | sed s:$:%\($ARC_ERR*$PARAM1\)/$ARC_ERR:g|bc| sort -n | uniq -c| awk 'OFS="," {print $2,$1}'>param1_wrapped.csv
cut -d ',' -f 2 < starline.txt | sed s:$:%\($ARC_ERR*$PARAM2\)/$ARC_ERR:g|bc| sort -n | uniq -c| awk 'OFS="," {print $2,$1}'>param2_wrapped.csv
cut -d ',' -f 3 < starline.txt | sed s:$:%\($ARC_ERR*$PARAM3\)/$ARC_ERR:g|bc| sort -n | uniq -c| awk 'OFS="," {print $2,$1}'>param3_wrapped.csv
