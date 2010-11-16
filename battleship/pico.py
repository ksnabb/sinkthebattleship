from xml.sax import parseString
from xml.sax import SAXParseException
from xml.sax.handler import ContentHandler
from django.core.cache import cache
import urllib
import time
import json
import math
import threading

"""
http://10.10.10.254:8081/feed/danceroom
http://localhost:8000/pico
"""


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

    The feed is saved into the cache with the key <room_name>
    """
    
    def __init__(self, pico_server_url):
        self.dictionary = {}
        self.current_room = ""
        self.current_cluster = ""
        self.pico_server_url = pico_server_url
    
    def startElement(self, name, attrs):
    
        if(name == "room"):
            self.current_room = attrs.getValue("id")
            self.dictionary[self.current_room] = {}
                
        elif(name == "cluster"):
            self.current_cluster = attrs.getValue("id")
            self.dictionary[self.current_room][self.current_cluster] = \
                            {"id": self.current_cluster,
                            "x": math.trunc(float(attrs.getValue("x")) * 200),
                            "y": math.trunc(float(attrs.getValue("y")) * 200),
                            "vx": math.trunc(float(attrs.getValue("vx")) * 200),
                            "vy": math.trunc(float(attrs.getValue("vy")) * 200),
                            "sensors": []}
           
        elif(name == "m"):
            if self.current_room == "" or self.current_cluster == "":
                pass
            else:
                self.dictionary[self.current_room][self.current_cluster]["sensors"].append(attrs.getValue("id"))
        elif(name == "clutter"):
            self.current_cluster = ""
            pass
        
    def endElement(self, name):
        if(name == "cluster"):
            cache.set(self.pico_server_url + "/feed/" + self.current_room, 
                    json.dumps(self.dictionary))
            print "set into cache"
            print self.pico_server_url + "/feed/" + self.current_room
            print cache.get(self.current_room)

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

    The room info is saved into the cache with the key "<room_name>_info"
    """

    def __init__(self, pico_server_url):
        self.current_sensor = {}
        self.room_name = ""
        self.room_sensors = []
        self.last_x = 0
        self.last_y = 0
        self.pico_server_url = pico_server_url

    def startElement(self, name, attrs):

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

            
        
    def endElement(self, name):

        if name == "sensor":
            self.room_sensors.append(self.current_sensor)
        elif name == "room":
            res_dict = {
                "room_name": self.room_name,
                "room_sensors": self.room_sensors
                }
            cache.set(self.pico_server_url + "/info/" + self.room_name, 
                    json.dumps(res_dict))
            print "set into cache"
            print self.pico_server_url + "/info/" + self.room_name
            print cache.get(self.pico_server_url + "/info/" + self.room_name)


def get_rooms(pico_server_url):
    """
    this function returns the list
    of the rooms available at the pico server given
    """
    con = urllib.urlopen(pico_server_url + "/rooms")
    cache.set("rooms", con.read())
    return con.read()

def get_room_info(pico_server_url, room):
    """
    This functions returns the information of the
    given room at the pico server given
    """
    con = urllib.urlopen(pico_server_url + "/info/" + room)
    xml = con.read()
    handler = PicoRoomHandler(pico_server_url)
    parseString(xml, handler)
    return xml


def get_feed(pico_server_url, room):
    """
    This function returns a http ?! feed
    for the room given as parameter 

    the pico_server_url is the pico servers url to connect to
    """
    con = urllib.urlopen(pico_server_url + "/feed/" + room)
    last = ""
    increment = ""
    handler = PicoFeedHandler(pico_server_url)
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
                pass
            increment = ""
            time.sleep(0.5)
     
class PicoFeedReader(threading.Thread):
    def __init__(self, pico_server_url, room, name="picofeed"):
        threading.Thread.__init__(self, name=name)
        self.pico_server_url = pico_server_url
        self.room = room

    def run(self):
        print "start pico feed reader thread"
        for line in get_feed(self.pico_server_url, self.room):
            print line
        
