
#
#     m a i n . p y 
#
#     The Fountain project
#    
#     Last revision: IH240221
#
#


import ipaddress
import os
import sched
import time
import supervisor
#  import adafruit_ntp   #IH40122 this is abandoned since it would require opening the 123 port
from adafruit_httpserver import Request, Response


from FountainHTTPServer import FountainHTTPServer
from  FountainShowScheduler import FountainShowScheduler
from FountainSimulatedRTC import FountainSimulatedRTC
from boardResources import boardLED, FountainDeviceCollection, timeResolutionMilliseconds
from FountainApplicationData import fountainApp, debugPrint, timeToHMS
from FountainDeviceStatusVisualizer import FountainDeviceStatusVisualizer


fountainApp["version"]                  = "240221a"
fountainApp["verboseLevel"]             = 1 
fountainApp["simulated"]                = True

fountainDeviceCollection = FountainDeviceCollection()
fountainApp["fountainDeviceCollection"] = fountainDeviceCollection

ipv4    =  ipaddress.IPv4Address("192.168.0.110")     #IH231211 "192.168.0.110" works in BA
# ipv4    =  ipaddress.IPv4Address("192.168.0.195")     #IH231219 "192.168.0.195" works in W
# ipv4    =  ipaddress.IPv4Address("192.168.1.30")     #IH231219 "192.168.1.30" works in BV

netmask =  ipaddress.IPv4Address("255.255.255.0")     #IH231211 works in BA, W, BV
gateway =  ipaddress.IPv4Address("192.168.0.1")       #IH231211 works in BA, W, BV



debugPrint(1,f"Verbose level {fountainApp["verboseLevel"]}")
fountainDeviceStatusVisualizer = FountainDeviceStatusVisualizer(1)
    
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
fountainApp["currentStatusString"] = "Idle"
fountainApp["currentShowScheduler"] = None

def runShow(showSchedule=FountainShowScheduler.TestSchedule()):
        debugPrint (2,f'SHOW started at T+{timeToHMS(time.time()-fountainApp["timeAtStart"])}')
        fountainApp["currentStatusString"] = "Show running"
        fountainShowScheduler  = FountainShowScheduler(
                showSchedule,
                startDelayMilliSeconds=1000,
                debug=True)
        fountainApp["currentShowScheduler"]=fountainShowScheduler
        heartBeadCounter=0
        cycleDurationMs_start = supervisor.ticks_ms()

        while not fountainShowScheduler.empty():                
                
                fountainHTTPServer.poll()

                #IH240219 simple heartbeat 
                if heartBeadCounter<20:  # FAST  heartbeat means: loop active, show running
                        heartBeadCounter+=1
                else:
                        fountainDeviceCollection.getDeviceFromNativeFormatID(FountainDeviceCollection.LED1).pwm_setConstant(FountainDeviceCollection.LED1,
                                pwm_percentage=100
                                if fountainDeviceCollection.getDeviceFromNativeFormatID(FountainDeviceCollection.LED1).getState("percentageValue")==0
                                else 0)
                        heartBeadCounter=0
                        fountainApp["recentCycleDurationMs"] = supervisor.ticks_ms() - cycleDurationMs_start
                cycleDurationMs_start = supervisor.ticks_ms()
                
                if FountainHTTPServer.commandFromWebClient in [ 
                                FountainHTTPServer.SHOW_STOP, 
                                FountainHTTPServer.LOOP_STOP, 
                                FountainHTTPServer.SHOW_SUBMIT_SCHEDULE]:
                        fountainShowScheduler.cleanSchedule()    # this effectively breaks the while loop
                if FountainHTTPServer.commandFromWebClient in [ 
                                FountainHTTPServer.LED1_ON, 
                                FountainHTTPServer.LED1_OFF]:
                       fountainDeviceCollection.getDeviceFromNativeFormatID(FountainDeviceCollection.LED1).pwm_setConstant(FountainDeviceCollection.LED1,
                                pwm_percentage=100 if FountainHTTPServer.commandFromWebClient==fountainHTTPServer.LED1_ON else 0)
                fountainShowScheduler.runNonblocking()
                fountainDeviceStatusVisualizer.showStatusAll()
                                       
                time.sleep(timeResolutionMilliseconds/1000)  #IH240108 heuristic 
                                                             # IH240221 currently set to 0


        fountainShowScheduler.runCleanup()
        fountainApp["currentShowScheduler"] = None
        debugPrint(2,f'SHOW finished at T+{timeToHMS(time.time()-fountainApp["timeAtStart"])}')
        fountainApp["currentStatusString"] = "Idle"
        # FountainHTTPServer.commandFromWebClient may still contain recently assigned value
        # this will be processed in the higher-level loop



loopEnabled = True
fountainApp['currentScheduleNative']=FountainShowScheduler.TestSchedule()
heartBeadCounter=0
cycleDurationMs_start = supervisor.ticks_ms()
while True:
    try:
        fountainHTTPServer.poll()

        #IH240219 simple heartbeat 
        if heartBeadCounter<300:    # SLOW  heartbeat means: loop active, show not running
                heartBeadCounter+=1
        else:
                fountainDeviceCollection.getDeviceFromNativeFormatID(FountainDeviceCollection.LED1).pwm_setConstant(FountainDeviceCollection.LED1,
                        pwm_percentage=100
                        if fountainDeviceCollection.getDeviceFromNativeFormatID(FountainDeviceCollection.LED1).getState("percentageValue")==0
                                else 0)
                heartBeadCounter=0
                fountainApp["recentCycleDurationMs"] = supervisor.ticks_ms() - cycleDurationMs_start
        cycleDurationMs_start = supervisor.ticks_ms()


        if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.LED1_ON]:
                FountainHTTPServer.commandFromWebClient = None
                fountainDeviceCollection.getDeviceFromNativeFormatID(FountainDeviceCollection.LED1).pwm_setConstant(FountainDeviceCollection.LED1,pwm_percentage=100)
        if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.LED1_OFF]:
                FountainHTTPServer.commandFromWebClient = None
                fountainDeviceCollection.getDeviceFromNativeFormatID(FountainDeviceCollection.LED1).pwm_setConstant(FountainDeviceCollection.LED1,pwm_percentage=0)
        if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.LOOP_STOP]:
                loopEnabled = False 
                FountainHTTPServer.commandFromWebClient = None
                debugPrint (2,f'LOOP stopped at T+{timeToHMS(time.time()-fountainApp["timeAtStart"])}')
                fountainApp["currentStatusString"] = "Idle, loop stopped"
        if loopEnabled:
                fountainGlobalScheduler.run(blocking=False)
                fountainApp["currentStatusString"] = "Idle, loop active"
        if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.LOOP_START]:
                loopEnabled = True 
                FountainHTTPServer.commandFromWebClient = None
                debugPrint (2,f'LOOP started at T+{timeToHMS(time.time()-fountainApp["timeAtStart"])}')
        if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.SHOW_SUBMIT_SCHEDULE]:
                FountainHTTPServer.commandFromWebClient = None
                debugPrint(2,'fountainGlobalScheduler: new schedule loaded: ')
                debugPrint(2,FountainHTTPServer.kwargsFromWebClient['show_schedule'])       
                if FountainShowScheduler.validateSchedule(FountainHTTPServer.kwargsFromWebClient['show_schedule']):
                       fountainApp['currentScheduleNative'] = FountainShowScheduler.convertScheduleToNative(
                              FountainHTTPServer.kwargsFromWebClient['show_schedule'])[0]  #the first element of the tuple is the schedule
                       debugPrint(2,'fountainGlobalScheduler: schedule validated.')
                else:
                       fountainApp['currentScheduleNative'] = FountainShowScheduler.DefaultSchedule()
                       debugPrint(2,'fountainGlobalScheduler: schedule validation failed. Default schedule loaded.')  
                loopEnabled = False 
                fountainGlobalScheduler.cleanSchedule()
                debugPrint(2,'fountainGlobalScheduler: waiting for LOOP_START command')
                fountainApp["currentStatusString"] = "Idle, loop stopped"
        if loopEnabled and fountainGlobalScheduler.empty():
                # schedule next Show
                nextScheduledTime = time.time() + 10  #IH240124 TODO the time daly between shows to be set from HTTP server 
                debugPrint(2,f'fountainGlobalScheduler: next show scheduled to T+{timeToHMS(nextScheduledTime-fountainApp["timeAtStart"])} (current time is T+{timeToHMS(time.time()-fountainApp["timeAtStart"])})')
                # print(f'current NTP time is {fountainHTTPServer.getNTPdatetime()}') #IH240111 does not work due to disabled port 123
                fountainGlobalScheduler.enterabs(nextScheduledTime,1,runShow,kwargs={'showSchedule':fountainApp['currentScheduleNative']})
                # runShow may leave a commandFromWebClient pending
                #IH240124 HACK 
                if FountainHTTPServer.commandFromWebClient in [FountainHTTPServer.SHOW_STOP]:
                       FountainHTTPServer.commandFromWebClient = None
                                  
        fountainDeviceStatusVisualizer.showStatusAll()                                  

        time.sleep(timeResolutionMilliseconds/1000)  #IH240108 heuristic, 
                                                     # IH240221 currently set to 0

     
    except Exception as e:
        debugPrint(1,e)
        continue

        
        