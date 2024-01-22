
#
#    c o d e . p y 
#
#    The Fountain project
#    
#     Last revision: IH240122
#
#



import ipaddress
import os
import sched
import time
import adafruit_ntp
from adafruit_httpserver import Request, Response


from FountainHTTPServer import FountainHTTPServer
from  FountainShowScheduler import FountainShowScheduler
from boardResources import boardLED, FountainDevice, fountainSimulated, timeResolutionMilliseconds



# ipv4    =  ipaddress.IPv4Address("192.168.0.110")     #IH231211 "192.168.0.110" works in BA
# ipv4    =  ipaddress.IPv4Address("192.168.0.195")     #IH231219 "192.168.0.195" works in W
ipv4    =  ipaddress.IPv4Address("192.168.1.30")     #IH231219 "192.168.1.30" works in BV

netmask =  ipaddress.IPv4Address("255.255.255.0")     #IH231211 works in BA, W, BV
gateway =  ipaddress.IPv4Address("192.168.0.1")       #IH231211 works in BA, W, BV


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
                if FountainHTTPServer.commandFromWebClient is not None:
                        if FountainHTTPServer.commandFromWebClient==FountainHTTPServer.SHOW_STOP:
                                fountainShowScheduler.cleanSchedule()
                        if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.LOOP_STOP, FountainHTTPServer.SHOW_SUBMIT_SCHEDULE]:
                                fountainShowScheduler.cleanSchedule()    
                                FountainHTTPServer.commandFromWebClient = None      
                fountainShowScheduler.runNonblocking()
                time.sleep(timeResolutionMilliseconds/1000*2)  #IH240108 heuristic 
        print (f'SHOW finished at T+{timeToHMS(time.time()-timeAtStart)}')

def timeToHMS(timeSeconds):
        # see https://www.geeksforgeeks.org/python-program-to-convert-seconds-into-hours-minutes-and-seconds/
        min,sec = divmod(timeSeconds,60)
        hour,min = divmod(min,60)
        return '%d:%02d:%02d' % (hour,min,sec)

timeAtStart = time.time()
loopEnabled = True
currentSchedule = FountainShowScheduler.TestSchedule()
while True:
    try:
        fountainHTTPServer.poll()
        if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.LOOP_STOP]:
                loopEnabled = False 
                FountainHTTPServer.commandFromWebClient = None
                print (f'LOOP stopped at T+{timeToHMS(time.time()-timeAtStart)}')
        if loopEnabled:
                fountainGlobalScheduler.run(blocking=False)
        if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.LOOP_START]:
                loopEnabled = True 
                FountainHTTPServer.commandFromWebClient = None
        if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.SHOW_SUBMIT_SCHEDULE]:
                currentSchedule = FountainShowScheduler.TestSchedule()  # IH240119 for debugging only
                # IH240122 TODO set the new schedule from web client
                # IH240119 prepared to set the new schedule from web client        
                FountainHTTPServer.commandFromWebClient = None
                print('fountainGlobalScheduler: new schedule loaded')
                loopEnabled = False 
                print('fountainGlobalScheduler: waiting for LOOP_START command')
        if loopEnabled and fountainGlobalScheduler.empty():
                # schedule next Show
                nextScheduledTime = time.time() + 10
                print(f'fountainGlobalScheduler: next show scheduled to T+{timeToHMS(nextScheduledTime-timeAtStart)}')
                # print(f'current NTP time is {fountainHTTPServer.getNTPdatetime()}') #IH240111 does not work due to disabled port 123
                fountainGlobalScheduler.enterabs(nextScheduledTime,1,runShow,kwargs={'showSchedule':currentSchedule})
                # runShow may leave a commandFromWebClient pending
                                  
        time.sleep(timeResolutionMilliseconds/1000*2)  #IH240108 heuristic
     
    except Exception as e:
        print(e)
        continue
