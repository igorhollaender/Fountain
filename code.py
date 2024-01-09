
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
        print (f'SHOW started at T+{timeToHMS(time.time()-timeAtStart)}')
        fountainShowScheduler  = FountainShowScheduler(
                showSchedule,
                startDelayMilliSeconds=1000,
                debug=True)
        while not fountainShowScheduler.empty():
                fountainHTTPServer.poll()
                fountainShowScheduler.runNonblocking()
                time.sleep(timeResolutionMilliseconds/1000*2)  #IH240108 heuristic 
        print (f'SHOW finished at T+{timeToHMS(time.time()-timeAtStart)}')

def timeToHMS(timeSeconds):
        # see https://www.geeksforgeeks.org/python-program-to-convert-seconds-into-hours-minutes-and-seconds/
        min,sec = divmod(timeSeconds,60)
        hour,min = divmod(min,60)
        return '%d:%02d:%02d' % (hour,min,sec)

timeAtStart = time.time()
while True:
    try:
        fountainHTTPServer.poll()
        fountainGlobalScheduler.run(blocking=False)
        if fountainGlobalScheduler.empty():
                # schedule next Show
                nextScheduledTime = time.time() + 10
                print(f'fountainGlobalScheduler: next show scheduled to T+{timeToHMS(nextScheduledTime-timeAtStart)}')
                fountainGlobalScheduler.enterabs(nextScheduledTime,1,runShow,kwargs={'showSchedule':FountainShowScheduler.TestSchedule()})

        time.sleep(timeResolutionMilliseconds/1000*2)  #IH240108 heuristic
     
    except Exception as e:
        print(e)
        continue
