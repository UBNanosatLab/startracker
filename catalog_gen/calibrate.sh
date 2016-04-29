#!/bin/sh
EXT="`echo \"$@\" | grep -o [^\.]*$`"
cp "$@" calibration/image.$EXT
cd calibration
solve-field --overwrite --no-plots -vv  image.$EXT | grep "[0-9]" > image.txt
grep "^RMS error" image.txt | tail -n 1 | grep -o "[0-9].*[0-9]"| sed 's/^/ARC_ERR=/' >calibration.txt
grep -o "image size.*" image.txt| tail -n 1 | grep -o "[0-9].*[0-9]"| sed 's/^/IMG_X=/;s/ x /\nIMG_Y=/' >> calibration.txt
grep -o "^Pixel scale.*" image.txt| tail -n 1 | grep -o "[0-9].*[0-9]"| sed 's/^/ARC_PER_PIX=/' >> calibration.txt
grep -o "^Field size:.*" image.txt | tail -n 1 | grep -o "[0-9].*[0-9]"| sed 's/^/DEG_X=/;s/ x /\nDEG_Y=/' >> calibration.txt
rm image.*
