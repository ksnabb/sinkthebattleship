from xml.sax import parse
from xml.sax.handler import ContentHandler
import urllib

"""
http://10.10.10.254:8081/feed/danceroom
http://localhost:8000/pico
"""

PICO_URL = "http://10.10.10.254:8081"

class pico_feed_handler(ContentHandler):
    
    def startDocument():
        print "start document"
    
    def startElement(name, attrs):
        print "start element"
        print name
        print attrs
        
    def endElement(name):
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
    pass

def get_feed(room):
    """
    This function returns a http ?! feed
    for the room given as parameter
    """
    pass

