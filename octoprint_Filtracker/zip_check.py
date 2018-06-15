#!/bin/bash
if [ -e /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/master.zip ]; then
    
    sudo rm -rf /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/master.zip*
    sudo rm -rf /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/locbit-edge-master

fi
