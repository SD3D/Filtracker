from SimpleCV import Color, Camera, Display, JpegStreamCamera
import time
import timeout_decorator
import sys

TIMEOUT_SECONDS = 15

@timeout_decorator.timeout(TIMEOUT_SECONDS)
def scan(camera_base_url='http://octopi.local'):
    jc = JpegStreamCamera("{}/webcam/?action=stream".format(camera_base_url))
    qrcode = []

    horizontal_flip = True
    
    while(not qrcode):
        img_og = jc.getImage() #gets image from the camera

        img = img_og

        if horizontal_flip:
            img = img_og.flipHorizontal()
            horizontal_flip = False
        else:
            horizontal_flip = True

        qrcode = img.findBarcode() #finds qr data from image

        if(qrcode is not None): #if there is some data processed
            qrcode = qrcode[0]
            result = str(qrcode.data)
            return result #returns result of qr in python shell
