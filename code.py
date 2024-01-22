
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
#  import adafruit_ntp   #IH40122 this is abandoned since it would require opening the 123 port
from adafruit_httpserver import Request, Response



from FountainHTTPServer import FountainHTTPServer
from  FountainShowScheduler import FountainShowScheduler
from FountainSimulatedRTC import FountainSimulatedRTC
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

# IH240122 PROBLEM HERE this does not work
# fountainSimulatedRTC = FountainSimulatedRTC(
#         os.getenv('CIRCUITPY_WIFI_SSID'),
#         os.getenv('CIRCUITPY_WIFI_PASSWORD'),
#         debug=True)


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

        
        
        
'''





# SPDX-FileCopyrightText: 2021 jfabernathy for Adafruit Industries
# SPDX-License-Identifier: MIT

# adafruit_requests usage with a CircuitPython socket
# this has been tested with Adafruit Metro ESP32-S2 Express

import ssl
import wifi
import socketpool
import os

import adafruit_requests as requests

secrets = {}
secrets["ssid"] = os.getenv('CIRCUITPY_WIFI_SSID')
secrets["password"] = os.getenv('CIRCUITPY_WIFI_PASSWORD')

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)

socket = socketpool.SocketPool(wifi.radio)
https = requests.Session(socket, ssl.create_default_context())

TEXT_URL = "https://httpbin.org/get"
JSON_GET_URL = "https://httpbin.org/get"
JSON_POST_URL = "https://httpbin.org/post"

print("Fetching text from %s" % TEXT_URL)
response = https.get(TEXT_URL)
print("-" * 40)
print("Text Response: ", response.text)
print("-" * 40)
response.close()

print("Fetching JSON data from %s" % JSON_GET_URL)
response = https.get(JSON_GET_URL)
print("-" * 40)

print("JSON Response: ", response.json())
print("-" * 40)

data = "31F"
print("POSTing data to {0}: {1}".format(JSON_POST_URL, data))
response = https.post(JSON_POST_URL, data=data)
print("-" * 40)

json_resp = response.json()
# Parse out the 'data' key from json_resp dict.
print("Data received from server:", json_resp["data"])
print("-" * 40)

json_data = {"Date": "July 25, 2019"}
print("POSTing data to {0}: {1}".format(JSON_POST_URL, json_data))
response = https.post(JSON_POST_URL, json=json_data)
print("-" * 40)

json_resp = response.json()
# Parse out the 'json' key from json_resp dict.
print("JSON Data received from server:", json_resp["json"])
print("-" * 40)

'''