

#!/bin/sh
while :; do wget http://muri1.eng.buffalo.edu:8080/webcam.png -q -O webcam.png>/dev/null;  echo webcam.png; sleep 1;done | python startracker.py
