from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('battleship.views',
    # Example:
    url(r'^test/', 
        'test_page',
        name="test"),
    url(r'^room_clusters/', 
        'room_clusters',
        name="room_clusters"),
)
