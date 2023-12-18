
#
#    c o d e . p y 
#
#    The Fountain project
#    
#     Last revision: IH231211
#
#




import ipaddress
import os
import sched
import time
from adafruit_httpserver import Request, Response


from fountainHTTPServer import FountainHTTPServer
import fountainShowScheduler
from boardResources import boardLED

 
ipv4    =  ipaddress.IPv4Address("192.168.0.110")     #IH231211 "192.168.0.110" works in BA
netmask =  ipaddress.IPv4Address("255.255.255.0")     #IH231211 not sure
gateway =  ipaddress.IPv4Address("192.168.0.1")       #IH231211 not sure

       
fountainHTTPServer = FountainHTTPServer(
        os.getenv('CIRCUITPY_WIFI_SSID'),
        os.getenv('CIRCUITPY_WIFI_PASSWORD'),
        ipv4,
        netmask,
        gateway,
        debug=True)


clock = time.monotonic()
fountainHTTPServer.Start()
while True:
    try:
        fountainHTTPServer.poll()
        time.sleep(1)
    except Exception as e:
        print(e)
        continue
        