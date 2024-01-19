#
#    f o u n t a i n   H T T P   S e r v e r . p y 
#
#    Last revision: IH240119
#
#
#    based on 
#    https://learn.adafruit.com/pico-w-http-server-with-circuitpython/code-the-pico-w-http-server
#
#         SPDX-FileCopyrightText: 2023 Liz Clark for Adafruit Industries
#         SPDX-License-Identifier: MIT

import board
import microcontroller
import os
import socketpool
import time
import wifi
import adafruit_ntp

from adafruit_httpserver import Server, Request, Response, Route, GET, POST
from boardResources import boardLED



class FountainHTTPServer():

    # Commands from web client
    SHOW_START              = 1
    SHOW_STOP               = 2
    SHOW_SUBMIT_SCHEDULE    = 3
    LOOP_START              = 4
    LOOP_STOP               = 5
    
    #IH2410112 class variables  (for singleton only)
    commandFromWebClient = None
    kwargsFromWebClient = {}
    
    def __init__(
                self, 
                wifi_ssid, 
                wifi_password, 
                ipv4,
                netmask,
                gateway,
                debug=True) -> None:

        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.ipv4 = ipv4
        self.netmask = netmask
        self.gateway = gateway

        self.debug = debug
        self.server = None

            

    def Start(self):
        
        #  connect to network
        print()
        print("Connecting to WiFi")
        print(f"SSID:     {self.wifi_ssid}")
        print(f"Password: {self.wifi_password}")

        #  set static IP address
        wifi.radio.set_ipv4_address(ipv4=self.ipv4,netmask=self.netmask,gateway=self.gateway)

        #  connect to your SSID
        wifi.radio.connect(self.wifi_ssid, self.wifi_password)

        print("Connected to WiFi")
        pool = socketpool.SocketPool(wifi.radio)
        self.server = Server(pool, "/static", debug=self.debug)
     
        # IH240111 HACK the NTP included
        self.ntp = adafruit_ntp.NTP(pool)
        
        # add routes
        self.server.add_routes([
                Route("/",GET, FountainHTTPServer.base),
                Route("/",POST, FountainHTTPServer.buttonpress),
        ])
        

        print("starting server..")
        # startup the server
        try:
            self.server.start(str(wifi.radio.ipv4_address))
            print("Listening on http://%s:80" % wifi.radio.ipv4_address)
        #  if the server fails to begin, restart 
        except OSError:
            time.sleep(5)
            print("restarting..")
            microcontroller.reset() 

            
    def poll(self):
        self.server.poll()


    def getNTPdatetime(self):
        return self.ntp.datetime() #IH240111 PROBLEM this does not work (-2,"Name or service not known")
    
    #  route request processing functions

    @staticmethod
    def base(request: Request):
        #  serve the HTML f string
        #  with content type text/html
        return Response(request, f"{FountainHTTPServer.Webpage()}", content_type='text/html')
    
    @staticmethod
    def buttonpress(request: Request):
        #  get the raw text
        raw_text = request.raw_request.decode("utf8")
        print(f'raw_text is "{raw_text}"')
        #  if the led on button was pressed
        if "ON" in raw_text:
            boardLED.value = True
        #  if the led off button was pressed
        if "OFF" in raw_text:
            boardLED.value = False
        #  stop current show (but continue loop)
        if "SHOW_STOP" in raw_text:
            FountainHTTPServer.commandFromWebClient = FountainHTTPServer.SHOW_STOP
            FountainHTTPServer.kwargsFromWebClient = {}
        #  reload site
        return Response(request, f"{FountainHTTPServer.Webpage()}", content_type='text/html')

    @staticmethod
    def Webpage():
        font_family = "monospace"
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta http-equiv="Content-type" content="text/html;charset=utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
        html {{
            font-family: {font_family}; 
            background-color: lightgrey;
            display:inline-block; 
            margin: 0px auto; 
            text-align: center;
            }}
        
        h1 {{
            color: deeppink; 
            width: 200; 
            word-wrap: break-word; 
            padding: 2vh; 
            font-size: 35px
            ;}}
        
        p {{
            font-size: 1.5rem; 
            width: 200; 
            word-wrap: break-word;
            }}
        
        .button {{
            font-family: {font_family};^
            display: inline-block;
            background-color: black; 
            border: none;
            border-radius: 4px; 
            color: white; 
            padding: 16px 40px;
            text-decoration: none; 
            font-size: 30px; 
            margin: 2px; 
            cursor: pointer;
            }}

        .textbox {{
            font-family: {font_family};
            font-size: 1.0rem;
            height:  200px;
            width:  80%;
            }}

        p.dotted {{
            margin: auto;
            width: 75%; 
            font-size: 25px; 
            text-align: center;
            }}
        </style>
        </head>

        <body>
        <title>Fountain HTTP Server</title>
        <h1>Fountain HTTP Server</h1>
        
        
        <form accept-charset="utf-8" method="POST">
        <p>
        <button class="button" name="LED ON" value="ON" type="submit">LED ON</button>
        <button class="button" name="LED OFF" value="OFF" type="submit">LED OFF</button>
        </p>
        <p>
        <button class="button" name="BUTTON_SHOW_STOP" value="SHOW_STOP" type="submit">STOP SHOW</button>
        <button class="button" name="BUTTON_LOOP_STOP" value="LOOP_STOP" type="submit">STOP LOOP</button>
        <button class="button" name="BUTTON_LOOP_START" value="LOOP_START" type="submit">START LOOP</button>
        </p>
        </p>
        </form>

        <form accept-charset="utf-8" method="POST">
        <p>
        <input class="textbox" name="TEXTBOX_SHOW_SCHEDULE" value="abcdef" ></input>
        </p>
        <p>
        <button class="button" name="SHOW_SUBMIT_SCHEDULE" value="SHOW_SUBMIT_SCHEDULE" type="submit">SUBMIT SHOW SCHEDULE</button>
        </p>
        </form>
        
        </body></html>
        """
        return html