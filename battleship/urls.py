from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('battleship.views',
    # Example:
    url(r'^room/(?P<room_name>\w+)/$', 
        'room',
        name="room"),
    url(r'^room_clusters/(?P<room_name>\w+)/$', 
        'room_clusters',
        name="room_clusters"),
)
