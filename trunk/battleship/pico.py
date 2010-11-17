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

    room:
    {
    "id": "<room_id>",
    "clusters" : <array of clusters>
    }

    cluster in array of clusters:
    {
    "<cluster_id>": {
            "id": "<id of cluster>",
            "x": <x coordinate of cluster>,
            "y": <y coordingate of cluster>,
            "vx": <x speed of cluster>,
            "vy": <y speed of cluster>,
            "magnitude": <magnitude of the cluster>,
            "size": <size of the cluster>,
            "sensors": <array of sensors>
        }
    }

    sensor in array of sensors:
    {
        "id": "<id of sensor>",
        "value": <value of sensor>
    }

    The feed is saved into the cache with the key <room_name>
    """
    
    def __init__(self, pico_server_url):
        self.room_id = ""
        self.room_clusters = []
        self.cluster_id = ""
        self.cluster_x = ""
        self.cluster_y = ""
        self.cluster_vx = ""
        self.cluster_vy = ""
        self.cluster_magnitude = ""
        self.cluster_size = ""
        self.cluster_sensors = []
        self.sensor_id = ""
        self.sensor_value = ""
        self.pico_server_url = pico_server_url
    
    def startElement(self, name, attrs):
    
        if(name == "room"):
            self.room_id = attrs.getValue("id")
            self.room_clusters = []
                
        elif(name == "cluster"):
            self.cluster_id = attrs.getValue("id")
            self.cluster_x = math.trunc(float(attrs.getValue("x")) * 100)
            self.cluster_y = math.trunc(float(attrs.getValue("y")) * 100)
            self.cluster_vx = math.trunc(float(attrs.getValue("vx")) * 100)
            self.cluster_vy = math.trunc(float(attrs.getValue("vy")) * 100)
            self.cluster_magnitude = math.trunc(float(attrs.getValue("magnitude")) * 100)
            self.cluster_size = math.trunc(float(attrs.getValue("size")) * 100)
            self.cluster_sensors = []
          
        elif(name == "m"):
            self.sensor_id = attrs.getValue("id")
            self.sensor_value = math.trunc(float(attrs.getValue("value")) * 100)
        
    def endElement(self, name):
        if(name == "room"):
            room_dict = {
                    "id": self.room_id,
                    "clusters": self.room_clusters
                    }
            print "set into cache"
            print room_dict
            cache.set(self.pico_server_url + "/feed/" + self.room_id, 
                    json.dumps(room_dict))

        elif(name == "cluster"):
            cluster_dict = {
                        "id": self.cluster_id,
                        "x": self.cluster_x,
                        "y": self.cluster_y,
                        "vx": self.cluster_vx,
                        "vy": self.cluster_vy,
                        "magnitude": self.cluster_magnitude,
                        "size": self.cluster_size,
                        "sensors": self.cluster_sensors,
                        }
            self.room_clusters.append(cluster_dict)
        elif(name == "m"):
            self.cluster_sensors.append({
                                "id": self.sensor_id,
                                "value": self.sensor_value
                            })
            

class PicoRoomHandler(ContentHandler):
    """
    This handler handles the xml description from a pico server
    and saves it in JSON format to the django cache.

    The JSON format is mapped straight from the room xml
    file

    The JSON format takes the following format:
    {
    "id": <id of the room>,
    "plan": "<url to the room plan>",
    "sensors": [<array of room sensors>]
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
        self.room_id = ""
        self.room_plan = ""
        self.room_sensors = []
        self.sensor_id = ""
        self.sensor_x = 0
        self.sensor_y = 0
        self.pico_server_url = pico_server_url

    def startElement(self, name, attrs):
        if name == "room":
            self.room_id = attrs.getValue("id")
            self.room_plan = attrs.getValue("plan")
            self.room_sensors = []

        elif name == "sensor":
            self.sensor_id = attrs.getValue("id")
            self.sensor_x = math.trunc(float(attrs.getValue("x")) * 100)
            self.sensor_y = math.trunc(float(attrs.getValue("y")) * 100)


            
        
    def endElement(self, name):
        
        if name == "room":
            room_dict = {
                "id": self.room_id,
                "plan": self.room_plan,
                "sensors": self.room_sensors
                }
            print "set into cache"
            print room_dict
            cache.set(self.pico_server_url + "/info/" + self.room_id, 
                    json.dumps(room_dict))

        elif name == "sensor":
            self.room_sensors.append({
                                "id": self.sensor_id,
                                "x": self.sensor_x,
                                "y": self.sensor_y
                                })


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
        
