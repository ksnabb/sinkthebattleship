"""
The pico views is supposed to mimic a pico server
"""

from django.http import HttpResponse
from django.shortcuts import render_to_response
from xml.sax import parse
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import os
import sys
import time

def rooms(request):    
    return render_to_response('list_of_rooms.txt', mimetype='text/plain')

def info(request, room):
    return render_to_response('danceroom.xml', mimetype='text/xml')

def feed(request, room):
    return HttpResponse(xml_feed(), mimetype="text/xml")

def xml_feed():
    f = open(os.path.join(os.path.dirname(__file__), 'templates/test_feed.xml'))
    
    for line in f:
        yield line
        if "</room>" in line:
            time.sleep(1)
            
