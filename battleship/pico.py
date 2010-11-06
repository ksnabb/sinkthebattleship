from xml.sax import parseString
from xml.sax import SAXParseException
from xml.sax.handler import ContentHandler
from django.core.cache import cache
import urllib
import time
import json

"""
http://10.10.10.254:8081/feed/danceroom
http://localhost:8000/pico
"""

#PICO_URL = "http://10.10.10.254:8081"
PICO_URL = "http://127.0.0.1:8000/pico"


class PicoFeedHandler(ContentHandler):
    
    def __init__(self):
        self.dictionary = {}
        self.current_room = ""
        self.current_cluster = ""
    
    def startElement(self, name, attrs):
        print "start element"
    
        if(name == "room"):
            self.current_room = attrs.getValue("id")
            self.dictionary[self.current_room] = {}
                
        elif(name == "cluster"):
            self.current_cluster = attrs.getValue("id")
            self.dictionary[self.current_room][self.current_cluster] = \
                            {"id": self.current_cluster,
                            "x": attrs.getValue("x"),
                            "y": attrs.getValue("y"),
                            "vx": attrs.getValue("vx"),
                            "vy": attrs.getValue("vy")}
            cache.set(self.current_room, 
                    json.dumps(self.dictionary))
            print "set into cache"
            print self.current_room
            print cache.get(self.current_room)
           
        elif(name == "m"):
            pass
        elif(name == "clutter"):
            pass
        
    def endElement(self, name):
        print "end element"
        print name


def get_rooms():
    """
    this function returns the list
    of the rooms available
    """
    con = urllib.urlopen(PICO_URL + "/rooms")
    return con.read()

def get_room_info(room):
    """
    This functions returns the information of the
    given room
    """
    con = urllib.urlopen(PICO_URL + "/info/" + room)
    return con.read()

def get_feed(room):
    """
    This function returns a http ?! feed
    for the room given as parameter
    """
    con = urllib.urlopen(PICO_URL + "/feed/" + room)
    last = ""
    increment = ""
    handler = PicoFeedHandler()
    while True:
        character = con.read(1)
        last = last + character
        increment = increment + character
        
        if(len(last) == 8):
            last = last[1:8]
        
        if(last == "</room>"):
            yield(increment)
            try:
                parseString(increment, handler)
            except SAXParseException:
                print "SAXParseException"
                pass
            increment = ""
            time.sleep(0.5)
     

