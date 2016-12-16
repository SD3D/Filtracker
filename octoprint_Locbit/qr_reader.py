from SimpleCV import Color, Camera, Display, JpegStreamCamera


def scan():
    jc = JpegStreamCamera("http://octopi.local/webcam/?action=stream")
    qrcode = []
    while(not qrcode):
        img_og = jc.getImage() #gets image from the camera
        img = img_og
        qrcode = img.findBarcode() #finds qr data from image

        if(qrcode is not None): #if there is some data processed
            qrcode = qrcode[0]
            result = str(qrcode.data)
            return result #returns result of qr in python shell
