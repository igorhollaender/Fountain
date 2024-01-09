
#
#    c o d e . p y 
#
#    The Fountain project
#    
#     Last revision: IH240108
#
#



import ipaddress
import os
import sched
import time
from adafruit_httpserver import Request, Response


from FountainHTTPServer import FountainHTTPServer
from  FountainShowScheduler import FountainShowScheduler
from boardResources import boardLED, FountainDevice, fountainSimulated, timeResolutionMilliseconds



ipv4    =  ipaddress.IPv4Address("192.168.0.110")     #IH231211 "192.168.0.110" works in BA
# ipv4    =  ipaddress.IPv4Address("192.168.0.195")     #IH231219 "192.168.0.195" works in W
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

fountainGlobalScheduler = sched.scheduler(timefunc=time.time)
fountainHTTPServer.Start()


def runShow(showSchedule=FountainShowScheduler.TestSchedule()):
        fountainShowScheduler  = FountainShowScheduler(
                showSchedule,
                startDelayMilliSeconds=1000,
                debug=True)
        while not fountainShowScheduler.empty():
                fountainHTTPServer.poll()
                fountainShowScheduler.runNonblocking()
                time.sleep(timeResolutionMilliseconds/1000*2)  #IH240108 heuristic 
             

while True:
    try:
        fountainHTTPServer.poll()
        fountainGlobalScheduler.run(blocking=False)
        if fountainGlobalScheduler.empty():
                # schedule next Show
                fountainGlobalScheduler.enterabs(time.time()+10,1,runShow)  # IH240108 TODO: add arguments for runShow

        time.sleep(timeResolutionMilliseconds/1000*2)  #IH240108 heuristic
     
    except Exception as e:
        print(e)
        continue
