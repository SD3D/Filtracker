from SimpleCV import Color, Camera, Display, JpegStreamCamera

jc = JpegStreamCamera("http://octopi.local/webcam/?action=stream")
qrcode = []
print "Scanning..."
while(not qrcode):
    img_og = jc.getImage() #gets image from the camera
    img = img_og.flipHorizontal() #corrects image flip so qr can data can be read
    qrcode = img.findBarcode() #finds qr data from image

    if(qrcode is not None): #if there is some data processed
        qrcode = qrcode[0]
        result = str(qrcode.data)
        print result #prints result of qr in python shell