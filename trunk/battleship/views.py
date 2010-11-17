# Create your views here.
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render_to_response
from battleship.pico import get_room_info
from battleship.pico import PicoFeedReader
import json
import time
import settings
import threading

def test_page(request):
    return render_to_response('test.html')

def room(request, room_name):
    """
    This function return an html representation of the
    room requested.

    room_name -- The room to return the html presentation for
    """
    room_json = cache.get(settings.PICO_URL + "/info/" + room_name)

    if(room_json == None):
        get_room_info(settings.PICO_URL, room_name)
        room_json = cache.get(settings.PICO_URL + "/info/" + room_name)

    room_dict = json.loads(room_json)
    #do modifications to value here if needed

    return render_to_response("room.html", room_dict)
    
def room_clusters(request, room_name):
    """
    This function returns an JSON of the last cluster saved to
    the django cache for the room given.
    """
    client_clusters = request.GET
    if len(client_clusters.keys()) == 0:
        client_clusters = None
    else:
        client_clusters = client_clusters.keys()[0]
        
    server_clusters = cache.get(settings.PICO_URL + "/feed/" + room_name)
    print client_clusters
    print server_clusters

    print threading.enumerate()
    create_new_thread = True
    for t in threading.enumerate():
        if(t.getName() == room_name):
            create_new_thread = False
            break

    if(create_new_thread):
        cache.set(settings.PICO_URL + "/feed/" + room_name, 
                json.dumps({}))
        pfr = PicoFeedReader(settings.PICO_URL, room_name, name=room_name)
        pfr.start()

    while client_clusters == server_clusters:
        time.sleep(1)
        server_clusters = cache.get(settings.PICO_URL + "/feed/" + room_name)
        print client_clusters
        print server_clusters

    #do modifications to value here if needed
    
    return HttpResponse(server_clusters)
    
