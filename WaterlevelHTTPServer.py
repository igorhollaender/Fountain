#
#    W a t e r l e v e l   H T T P   S e r v e r . p y 
#
#    Last revision: IH250303
#
#
#   based on 
#   https://learn.adafruit.com/pico-w-http-server-with-circuitpython/code-the-pico-w-http-server
#
#         SPDX-FileCopyrightText: 2023 Liz Clark for Adafruit Industries
#         SPDX-License-Identifier: MIT
#
#   for websockets, see
#   https://docs.circuitpython.org/projects/httpserver/en/latest/examples.html#websockets
#
import board
import microcontroller
import os
import socketpool
import time
import wifi

import ssl
import adafruit_requests

from adafruit_httpserver import Server, Request, Response, Route, Websocket, GET, POST
from boardResources import boardLED
from WaterlevelApplicationData import waterlevelApp, debugPrint


class WaterlevelHTTPServer():

    # IH240115 for debugging only
    LED1_ON                 = 101
    LED1_OFF                = 102

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
                version,
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
        debugPrint(2,"")
        debugPrint(2,"Connecting to WiFi")
        debugPrint(2,f"SSID:     {self.wifi_ssid}")
        debugPrint(2,f"Password: {self.wifi_password}")

        #  set static IP address
        wifi.radio.set_ipv4_address(ipv4=self.ipv4,netmask=self.netmask,gateway=self.gateway)

        #  connect to your SSID
        wifi.radio.connect(self.wifi_ssid, self.wifi_password)

        debugPrint(2,"Connected to WiFi")
        self.pool = socketpool.SocketPool(wifi.radio)
        self.server = Server(self.pool, "/static", debug=self.debug)
     
        
        # add routes
        self.server.add_routes([
                Route("/",GET, WaterlevelHTTPServer.base),
                Route("/",POST, WaterlevelHTTPServer.buttonpress),
                Route("/connect-websocket",GET, WaterlevelHTTPServer.connect_client),
        ])
        

        debugPrint(2,"starting server..")
        # startup the server
        try:
            self.server.start(str(wifi.radio.ipv4_address))
            debugPrint(1,"Listening on http://%s:80" % wifi.radio.ipv4_address)
        #  if the server fails to begin, restart 
        except OSError:
            time.sleep(5)
            debugPrint(1,"restarting..")
            microcontroller.reset() 

            
    def poll(self):
        self.server.poll()


    def getSocket(self):
        '''
        this is used for other connections, for example FountainSimulatedRTC
        '''
        return self.pool
    

    @staticmethod
    def url_parse(url):
        """
        see https://stackoverflow.com/questions/16566069/url-decode-utf-8-in-python
        """
        l = len(url)
        data = bytearray()
        i = 0
        while i < l:
            if url[i] != '%':
                if url[i] == '+':  #IH240124 added
                    d = ord(' ')
                else:
                    d = ord(url[i])
                i += 1
            else:
                d = int(url[i+1:i+3], 16)
                i += 3
            data.append(d)
        return data.decode('utf8')
    
    #  route request processing functions

    @staticmethod
    def base(request: Request):
        #  serve the HTML f string
        #  with content type text/html
        return Response(request, f"{WaterlevelHTTPServer.Webpage()}", content_type='text/html')
    
    @staticmethod
    def buttonpress(request: Request):
        #  get the raw text
        #  raw_text = request.raw_request.decode("utf8")
        #  print(f'raw_text is "{raw_text}"')

        form_data = request.form_data
        debugPrint(2,f'form data is "{form_data}"')

        # for debugging
        if "BUTTON_LED_ON" in form_data:
            WaterlevelHTTPServer.commandFromWebClient = WaterlevelHTTPServer.LED1_ON
            WaterlevelHTTPServer.kwargsFromWebClient = {}
        #  if the led off button was pressed
        if "BUTTON_LED_OFF" in form_data:
            WaterlevelHTTPServer.commandFromWebClient = WaterlevelHTTPServer.LED1_OFF
            WaterlevelHTTPServer.kwargsFromWebClient = {}
        
        #  reload site
        return Response(request, f"{WaterlevelHTTPServer.Webpage()}", content_type='text/html')

    @staticmethod
    def connect_client(request: Request):
        if waterlevelApp["websocket"] is not None:
            waterlevelApp["websocket"].close()
        waterlevelApp["websocket"] = Websocket(request)
        return waterlevelApp["websocket"]
    
    @staticmethod
    def Webpage():
        font_family = "monospace"
        version = waterlevelApp['version']
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
            font-family: {font_family};
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
        .button:disabled {{
            background-color: grey; 
            }}

        .textarea {{
            font-family: {font_family};
            font-size: 1.0rem;
            width:  80%;
            height:  300px;
            }}

        p.dotted {{
            margin: auto;
            width: 75%; 
            font-size: 25px; 
            text-align: center;
            }}
        </style>
        </head>

        <script>
        var status_show_running;
        var status_loop_running;
        
        function UpdateUI() {{
            if (status_show_running){{
                document.getElementById("BUTTON_SHOW_STOP").disabled = false;
                document.getElementById("BUTTON_LOOP_STOP").disabled = false;
            }}
            if (status_loop_running){{
                document.getElementById("BUTTON_SHOW_STOP").disabled = false;
                document.getElementById("BUTTON_LOOP_STOP").disabled = false;
                document.getElementById("BUTTON_LOOP_START").disabled = true;
            }}
            else{{
                document.getElementById("BUTTON_SHOW_STOP").disabled = true;
                document.getElementById("BUTTON_LOOP_STOP").disabled = true;
                document.getElementById("BUTTON_LOOP_START").disabled = false;
            }}
        }}

        function SubmitCommand() {{
            // document.getElementById("FORM_BUTTON_CONTROLS").submit()
        }}

        function initialize_page() {{
            status_show_running=true;
            status_loop_running=true;
            UpdateUI();
        }}

        function led_control(turn_led_on){{SubmitCommand();}}
        function show_stop() {{status_show_running=false;UpdateUI();SubmitCommand();}}
        function loop_stop() {{status_loop_running=false;status_show_running=false;UpdateUI();SubmitCommand();}}
        function loop_start() {{status_loop_running=true;status_show_running=true;UpdateUI();SubmitCommand();}}
        function show_submit_schedule() {{status_loop_running=false;status_show_running=false;UpdateUI();SubmitCommand();}}
        </script>

        <body>
        <script>
            let ws = new WebSocket('ws://' + location.host + '/connect-websocket');
            ws.onopen = () => console.log('WebSocket connection opened');
            ws.onclose = () => console.log('WebSocket connection closed');
            ws.onmessage = () => console.log('MESSAGE COMES');
            ws.onerror = () => console.log('ERROR OCCURED');
        </script>
        <title>Waterlevel HTTP Server</title>
        <h1>Waterlevel HTTP Server Ver.{version}</h1>
        
    
        
        <form id="FORM_BUTTON_CONTROLS" accept-charset="utf-8" method="POST">
        <p>
        <button class="button" id="BUTTON_LED_ON"  name="BUTTON_LED_ON" type="submit" >LED ON</button>
        <button class="button" id="BUTTON_LED_OFF" name="BUTTON_LED_OFF" type="submit" >LED OFF</button>
        </p>
        <p>
        </p>
        </form>

        </body></html>
        """
        return html