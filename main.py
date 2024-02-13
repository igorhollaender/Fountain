
#
#     m a i n . p y 
#
#     The Fountain project
#    
#     Last revision: IH240212
#
#


import ipaddress
import os
import sched
import time
#  import adafruit_ntp   #IH40122 this is abandoned since it would require opening the 123 port
from adafruit_httpserver import Request, Response


from FountainHTTPServer import FountainHTTPServer
from  FountainShowScheduler import FountainShowScheduler
from FountainSimulatedRTC import FountainSimulatedRTC
from boardResources import boardLED, FountainDeviceCollection, timeResolutionMilliseconds
from FountainApplicationData import fountainApp, debugPrint, timeToHMS
from FountainDeviceStatusVisualizer import FountainDeviceStatusVisualizer


fountainApp["version"]                  = "240213a"
fountainApp["verboseLevel"]             = 2 
fountainApp["simulated"]                = True

fountainDeviceCollection = FountainDeviceCollection()
fountainApp["fountainDeviceCollection"] = fountainDeviceCollection

ipv4    =  ipaddress.IPv4Address("192.168.0.110")     #IH231211 "192.168.0.110" works in BA
# ipv4    =  ipaddress.IPv4Address("192.168.0.195")     #IH231219 "192.168.0.195" works in W
# ipv4    =  ipaddress.IPv4Address("192.168.1.30")     #IH231219 "192.168.1.30" works in BV

netmask =  ipaddress.IPv4Address("255.255.255.0")     #IH231211 works in BA, W, BV
gateway =  ipaddress.IPv4Address("192.168.0.1")       #IH231211 works in BA, W, BV



debugPrint(1,f"Verbose level {fountainApp["verboseLevel"]}")
fountainDeviceStatusVisualizer = FountainDeviceStatusVisualizer(0)
fountainApp["fountainDeviceStatusVisualizer"] = fountainDeviceStatusVisualizer

    
fountainHTTPServer = FountainHTTPServer(
        os.getenv('CIRCUITPY_WIFI_SSID'),
        os.getenv('CIRCUITPY_WIFI_PASSWORD'),
        ipv4,
        netmask,
        gateway,
        fountainApp['version'],
        debug=(True if fountainApp["verboseLevel"]>1 else False))

# IH240122 PROBLEM HERE this does not work 
# fountainSimulatedRTC = FountainSimulatedRTC(
#          os.getenv('CIRCUITPY_WIFI_SSID'),
#          os.getenv('CIRCUITPY_WIFI_PASSWORD'),
#          debug=True)


fountainGlobalScheduler = sched.scheduler(timefunc=time.time)
fountainHTTPServer.Start()
fountainApp["timeAtStart"] = time.time()

def runShow(showSchedule=FountainShowScheduler.TestSchedule()):
        debugPrint (2,f'SHOW started at T+{timeToHMS(time.time()-fountainApp["timeAtStart"])}')
        fountainShowScheduler  = FountainShowScheduler(
                showSchedule,
                startDelayMilliSeconds=1000,
                debug=True)
        while not fountainShowScheduler.empty():
                fountainHTTPServer.poll()
                if FountainHTTPServer.commandFromWebClient in [ 
                                FountainHTTPServer.SHOW_STOP, 
                                FountainHTTPServer.LOOP_STOP, 
                                FountainHTTPServer.SHOW_SUBMIT_SCHEDULE]:
                        fountainShowScheduler.cleanSchedule()    # this effectively breaks the while loop
                fountainShowScheduler.runNonblocking()
                fountainDeviceStatusVisualizer.showStatusAll()
                time.sleep(timeResolutionMilliseconds/1000*2)  #IH240108 heuristic 
        fountainShowScheduler.runCleanup()
        debugPrint(2,f'SHOW finished at T+{timeToHMS(time.time()-fountainApp["timeAtStart"])}')
        # FountainHTTPServer.commandFromWebClient may still contain recently assigned value
        # this will be processed in the higher-level loop



loopEnabled = True
currentSchedule = FountainShowScheduler.TestSchedule()
fountainApp['currentSchedule']=FountainShowScheduler.convertScheduleToSimple(currentSchedule)
while True:
    try:
        fountainHTTPServer.poll()
        if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.LOOP_STOP]:
                loopEnabled = False 
                FountainHTTPServer.commandFromWebClient = None
                debugPrint (2,f'LOOP stopped at T+{timeToHMS(time.time()-fountainApp["timeAtStart"])}')
        if loopEnabled:
                fountainGlobalScheduler.run(blocking=False)
        if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.LOOP_START]:
                loopEnabled = True 
                FountainHTTPServer.commandFromWebClient = None
                debugPrint (2,f'LOOP started at T+{timeToHMS(time.time()-fountainApp["timeAtStart"])}')
        if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.SHOW_SUBMIT_SCHEDULE]:
                FountainHTTPServer.commandFromWebClient = None
                debugPrint(2,'fountainGlobalScheduler: new schedule loaded: ')
                debugPrint(2,FountainHTTPServer.kwargsFromWebClient['show_schedule'])       
                if FountainShowScheduler.validateSchedule(FountainHTTPServer.kwargsFromWebClient['show_schedule']):
                       currentSchedule = FountainShowScheduler.convertScheduleToNative(
                              FountainHTTPServer.kwargsFromWebClient['show_schedule'])[0]  #the first element of the tuple is the schedule
                       debugPrint(2,'fountainGlobalScheduler: schedule validated.')
                else:
                       currentSchedule = FountainShowScheduler.DefaultSchedule()
                       debugPrint(2,'fountainGlobalScheduler: schedule validation failed. Default schedule loaded.')  
                fountainApp['currentSchedule']=FountainShowScheduler.convertScheduleToSimple(currentSchedule)
                loopEnabled = False 
                fountainGlobalScheduler.cleanSchedule()
                debugPrint(2,'fountainGlobalScheduler: waiting for LOOP_START command')
        if loopEnabled and fountainGlobalScheduler.empty():
                # schedule next Show
                nextScheduledTime = time.time() + 10  #IH240124 TODO the time daly between shows to be set from HTTP server 
                debugPrint(2,f'fountainGlobalScheduler: next show scheduled to T+{timeToHMS(nextScheduledTime-fountainApp["timeAtStart"])} (current time is T+{timeToHMS(time.time()-fountainApp["timeAtStart"])})')
                # print(f'current NTP time is {fountainHTTPServer.getNTPdatetime()}') #IH240111 does not work due to disabled port 123
                fountainGlobalScheduler.enterabs(nextScheduledTime,1,runShow,kwargs={'showSchedule':currentSchedule})
                # runShow may leave a commandFromWebClient pending
                #IH240124 HACK 
                if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.SHOW_STOP]:
                       FountainHTTPServer.commandFromWebClient = None
                                  
        fountainDeviceStatusVisualizer.showStatusAll()                                  
        time.sleep(timeResolutionMilliseconds/1000*2)  #IH240108 heuristic
     
    except Exception as e:
        debugPrint(1,e)
        continue

        
        