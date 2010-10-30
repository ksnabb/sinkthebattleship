"""
The pico views is supposed to mimic a pico server
"""

from django.http import HttpResponse
from django.shortcuts import render_to_response

import time

def rooms(request):    
    return HttpResponse("A304 A302")

def info(request, room):
    return render_to_response('room_info.xml', mimetype='text/xml')

def feed(request, room):
    return HttpResponse(xml_feed(), mimetype="text/xml")

def xml_feed():
    yield '<?xml version="1.0" encoding="iso-8859-1"?>'
    yield '<stream version="1.2">'

    for i in range(0,10):
        test_xml = '<room id="' + str(i) + '" time="117128848694"></room>'
        yield test_xml
        time.sleep(3)