

#!/bin/sh
while :; do wget http://muri1.eng.buffalo.edu:8080/webcam.png -q -O webcam.png>/dev/null;  echo beast/webcam.png; sleep 2;done | python startracker.py
