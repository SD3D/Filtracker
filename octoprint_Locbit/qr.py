#!/usr/bin/env python
import commands
import qr_reader
import os
import json
from timeout_decorator import TimeoutError
import sys

json_result = ''

try:
    horizontal_flip = False
    
    if len(sys.argv) >= 2 and sys.argv[1] == '-f':
        horizontal_flip = True

    json_result = json.dumps({'result': qr_reader.scan(horizontal_flip=horizontal_flip)})
except TimeoutError as e:
    json_result = json.dumps({'error': 'Timeout reading QR code. QR code not detected'})
except Exception as e:
    json_result = json.dumps({'error': "Error reading QR code: {}".format(str(e))})

print json_result
