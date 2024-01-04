
#
#    c o d e . p y 
#
#    The Fountain project
#    
#     Last revision: IH240104
#
#




import ipaddress
import os
import sched
import time
from adafruit_httpserver import Request, Response


from FountainHTTPServer import FountainHTTPServer
from  FountainShowScheduler import FountainShowScheduler
from boardResources import boardLED, FountainDevice

 
# globals

fountainSimulated = True


#  ipv4    =  ipaddress.IPv4Address("192.168.0.110")     #IH231211 "192.168.0.110" works in BA
ipv4    =  ipaddress.IPv4Address("192.168.0.195")     #IH231219 "192.168.0.195" works in W
#  ipv4    =  ipaddress.IPv4Address("192.168.1.30")     #IH231219 "192.168.1.30" works in BV

netmask =  ipaddress.IPv4Address("255.255.255.0")     #IH231211 works in BA, W
gateway =  ipaddress.IPv4Address("192.168.0.1")       #IH231211 works in BA, W


fountainDevice = FountainDevice()
       
fountainHTTPServer = FountainHTTPServer(
        os.getenv('CIRCUITPY_WIFI_SSID'),
        os.getenv('CIRCUITPY_WIFI_PASSWORD'),
        ipv4,
        netmask,
        gateway,
        debug=True)

fountainShowScheduler  = FountainShowScheduler(
        FountainShowScheduler.TestSchedule(),
        debug=True)



clock = time.monotonic()
fountainHTTPServer.Start()
while True:
    try:
        fountainHTTPServer.poll()
        # fountainShowScheduler.runNonblocking()
        time.sleep(1)
    except Exception as e:
        print(e)
        continue
        