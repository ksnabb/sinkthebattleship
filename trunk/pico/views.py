from django.http import HttpResponse
import time

def feed(request):
    return HttpResponse(xml_feed())

def xml_feed():
    yield '<?xml version="1.0" encoding="iso-8859-1"?>'
    yield '<stream version="1.2">'

    room = '<room id="I210" time="' + str(time.time()) + '">'
    for i in range(0,10):
        test_xml = "<div style='color:red; display: inline'> cell number " + str(i) + "</div>"
        yield test_xml
        time.sleep(3)
        
        
        
"""
<?xml version="1.0" encoding="iso-8859-1"?>
<stream version="1.2">
<room id="I210" time="117128848694">
<cluster id="4" name="" x="1.72" y="0.64" vx="0.14" vy="-0.17"
size="0.25" magnitude="211.00" zones="">
<m mcu="1" sid="35" id="79" value="91.00"/>
<m mcu="1" sid="34" id="78" value="120.00"/>
</cluster>
<cluster id="5" name="" x="1.79" y="2.21" vx="0.20" vy="0.01"
size="0.25" magnitude="83.00" zones="">
<m mcu="1" sid="41" id="65" value="73.00"/>
<m mcu="1" sid="40" id="64" value="10.00"/>
</cluster>
</room>

"""

