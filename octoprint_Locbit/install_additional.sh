#!/bin/bash

/usr/bin/apt-get update
/usr/bin/apt-get install -y ipython python-opencv python-scipy python-numpy python-setuptools python-pip python-pygame python-zbar
/usr/local/bin/pip install svgwrite https://github.com/sightmachine/SimpleCV/zipball/master timeout-decorator
/bin/chmod +x /home/pi/oprint/lib/python2.7/site-packages/octoprint_Locbit/qr.py
