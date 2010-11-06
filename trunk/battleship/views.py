# Create your views here.
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render_to_response


def test_page(request):
    return render_to_response('test.html')
    
def room_clusters(request):
    client_clusters = request.GET
    print client_clusters
    server_clusters = cache.get("danceroom")
    print server_clusters
    
    #if server_clusters == None:
    return HttpResponse("wait")
    #else:
    #   return HttpResponse(c)