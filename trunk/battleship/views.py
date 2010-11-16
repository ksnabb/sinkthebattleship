# Create your views here.
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render_to_response
from battleship.pico import get_room_info
import json
import time
import settings

def test_page(request):
    return render_to_response('test.html')

def room(request, room_name):
    """
    This function return an html representation of the
    room requested.

    room_name -- The room to return the html presentation for
    """
    print room_name
    room_json = cache.get(settings.PICO_URL + "/info/" + room_name)
    print room_json
    if(room_json == None):
        get_room_info(settings.PICO_URL, room_name)
        room_json = cache.get(settings.PICO_URL + "/info/" + room_name)
    print room_json
    return render_to_response("room.html", json.loads(room_json))
    
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
        
    server_clusters = cache.get("danceroom")
    print client_clusters
    print server_clusters
    
    while client_clusters == server_clusters:
        time.sleep(1)
        server_clusters = cache.get("danceroom")
        print client_clusters
        print server_clusters
    
    return HttpResponse(server_clusters)
    
