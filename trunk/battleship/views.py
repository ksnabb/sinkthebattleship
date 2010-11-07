# Create your views here.
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
import time

def test_page(request):
    return render_to_response('test.html')
    
def room_clusters(request):
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
    