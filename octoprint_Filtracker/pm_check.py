#!/bin/bash
sudo pm2 stop all
echo “Starting pm2...”
sudo pm2 start /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/locbit-edge-master/app.js