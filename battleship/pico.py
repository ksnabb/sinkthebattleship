from xml.sax import parseString
from xml.sax import SAXParseException
from xml.sax.handler import ContentHandler
from django.core.cache import cache
import urllib
import time
import json
import math

"""
http://10.10.10.254:8081/feed/danceroom
http://localhost:8000/pico
"""

#PICO_URL = "http://10.10.10.254:8081"
PICO_URL = "http://127.0.0.1:8080/pico"


class PicoFeedHandler(ContentHandler):
    """
    This handler handles a pico feed for a room
    
    The feed is saved as JSON into the django cache.

    The JSON is saved in the form:
    {
    "<room_name>": 
                {
                "<cluster_id>": {
                            "id": <id of cluster>,
                            "x": <x coordinate of cluster>,
                            "y": <y coordingate of cluster>,
                            "vx": <x speed of cluster>,
                            "vy": <y speed of cluster>
                        }
                }
    }
    """
    
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

class PicoRoomHandler(ContentHandler):
    """
    This handler handles the xml description from a pico server
    and saves it in JSON format to the django cache.

    The JSON format takes the following format:
    {
    "room_name": "<name of the room>",
    "room_sensors": [<array of room sensors>]
    }
    
    JSON for a sensor has the following format:
    {
    "id": <id of sensor>,
    "x": <x coordinate of sensor>,
    "y": <y coordinate of sensor>
    }
    """

    def __init__(self):
        self.current_sensor = {}
        self.room_name = ""
        self.room_sensors = []
        self.last_x = 0
        self.last_y = 0

    def startElement(self, name, attrs):
        print "start element"
        print name
        print attrs

        if name == "sensor":
            sensor_id = int(attrs.getValue("id"))
            sensor_x = math.trunc(float(attrs.getValue("x")) * 200)
            sensor_y = math.trunc(float(attrs.getValue("y")) * 200)

            self.current_sensor = {
                        "id": sensor_id, 
                        "x": sensor_x,
                        "y": sensor_y
                        }

        elif name == "room":
            self.room_name = attrs.getValue("id")
            print self.room_name

            
        
    def endElement(self, name):
        print "end element"
        print name
        if name == "sensor":
            self.room_sensors.append(self.current_sensor)
        elif name == "room":
            res_dict = {
                "room_name": self.room_name,
                "room_sensors": self.room_sensors
                }
            cache.set(self.room_name + "_info", 
                    json.dumps(res_dict))


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
    xml = con.read()
    handler = PicoRoomHandler()
    parseString(xml, handler)
    return xml

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
     

