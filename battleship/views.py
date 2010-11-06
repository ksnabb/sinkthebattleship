# Create your views here.
from django.core.cache import cache
from django.http import HttpResponse

def room_clusters(request):
    c = cache.get("danceroom")
    if c == None:
        return HttpResponse("wait")
    else:
        return HttpResponse(c)