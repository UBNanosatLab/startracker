#!/bin/sh
for i in `seq 1 $1`; do echo "" | bin/star_tracker_interface_test | grep saved | grep -o "/root/.*$"; done | ./run-startracker.sh
rm -i /root/flight-software/tests/data/Images/*.bmp
