#!/bin/bash
if [ -e /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/master.zip ];
then
    echo "master.zip is there"
    sudo rm -rf ~/oprint/lib/python2.7/site-packages/octoprint_Filtracker/master.zip*
    echo "Master zip files are gone."
else
    echo "master.zip is not there"
fi
if [ -e /etc/init.d/pm_check.sh ];
then
    echo "Running the pm2 start script."
    /etc/init.d/pm_check.sh
else
    echo "moving file to path."
    sudo cp /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/pm_check.py /etc/init.d/pm_check.sh
    echo "making script executable"
    chmod +x /etc/init.d/pm_check.sh
    echo"starting the script"
    /etc/init.d/pm_check.sh
    echo "ensuring the script executes on each system boot."
    update-rc.d /etc/init.d/mystartup.sh defaults 100
fi
if [ -e /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/zip_check.sh ];
then
    sudo rm -rf /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/zip_check.sh
fi
if [ -e /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/shell.sh ];
then
    sudo rm -rf /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/shell.sh
fi
if [ -e /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/pm_check.sh ];
then
    sudo rm -rf /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/pm_check.sh
fi
if [ -e /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/edge_set.sh ];
then
    sudo rm -rf /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/edge_set.sh
fi