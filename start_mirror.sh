#!/bin/bash
cd /home/pi/mirror/realsense_tracking

for (( ; ; ))
do
   echo "start narcissus"  >> /home/pi/mirror.output.txt 2>&1
   date                    >> /home/pi/mirror.output.txt 2>&1
   python narcissus.py noterm noscreen      >> /home/pi/mirror.output.txt 2>&1
   if test -f "/home/pi/mirror_stop"; then
	echo "mirror stops due to file"  >> /home/pi/mirror.output.txt 2>&1
	exit 0
   fi
done

# python narcissus.py
# add to crontab : @reboot /home/pi/mirror/start_mirror.sh > /home/pi/crontab_mirror_out.txt