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
    return render_to_response('room_info.xml', mimetype='text/xml')

def feed(request, room):
    return HttpResponse(xml_feed(), mimetype="text/xml")

def xml_feed():
    f = open(os.path.join(os.path.dirname(__file__), 'templates/test_feed.xml'))
    parser = make_parser()
    parser.setContentHandler(PicoFeedHandler())

    for line in f:
        yield line
        if "</room>" in line:
            time.sleep(3)
            
class PicoFeedHandler(ContentHandler):

    def startDocument(self):
        print "start document"
    
    def startElement(self, name, attrs):
        print "start element"
        print name
        print attrs
        
    def endElement(self, name):
        print "end element"
        print name
        if(name == "room"):
            time.sleep(3)
        
