#!/bin/sh

sudo apt-get remove -y --purge node 
sudo apt-get autoremove -y node 
echo "step 1"
sudo apt-get install -y nodejs global
sudo apt-get install -y npm global
sudo rm -rf /usr/bin/node > /dev/null 2>&1
echo "step 2"
sudo ln -s /usr/bin/nodejs /usr/bin/node
echo "step 3"
sudo npm update -g
echo "step 4"
echo "step 5"
sudo npm install --prefix /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/locbit-edge-master/ > /dev/null 2>&1
echo "step 6"
sudo npm install -g pm2@1.1.3
echo "step 7"
sudo pm2 start /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/locbit-edge-master/app.js
sudo pm2 startup systemd -u root
if [ -e /etc/init.d/pm_check.sh ]; then

    echo "Running the pm2 start script."
else
    echo "moving file to path."
    sudo cp /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/pm_check.py /etc/init.d/pm_check.sh
    echo "making script executable"
    sudo chmod +x /etc/init.d/pm_check.sh
    echo"starting the script"
    sudo /etc/init.d/pm_check.sh
    echo "ensuring the script executes on each system boot."
    sudo update-rc.d /etc/init.d/pm_check.sh defaults 100
fi