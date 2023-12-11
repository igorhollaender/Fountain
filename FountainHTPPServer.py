#
#    F o u n t a i n   H T T P   S e r v e r . p y 
#
#    Last revision: IH231211
#
#
#    based on 
#    https://learn.adafruit.com/pico-w-http-server-with-circuitpython/code-the-pico-w-http-server
#
#         SPDX-FileCopyrightText: 2023 Liz Clark for Adafruit Industries
#         SPDX-License-Identifier: MIT

import os
import time
import ipaddress
import wifi
import socketpool
import board
import microcontroller
from digitalio import DigitalInOut, Direction
from adafruit_httpserver import Server, Request, Response, POST


class FountainHTTPServer:

    def __init__(self, wifi_ssid, wifi_password,debug=True) -> None:

        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password

        self.debug = debug

        self.server = None
        
        #  onboard LED setup  - for basic functionality testing
        self.led = DigitalInOut(board.LED)
        self.led.direction = Direction.OUTPUT
        self.led.value = False

    def Start(self):
    
        #  connect to network
        print()
        print("Connecting to WiFi")
        print(f"SSID:     {self.wifi_ssid}")
        print(f"Password: {self.wifi_password}")

        #  set static IP address
        #IH231211 TODO make these to parameters
        self.ipv4    =  ipaddress.IPv4Address("192.168.0.110")   #IH231211 "192.168.0.110" works in BA
        self.netmask =  ipaddress.IPv4Address("255.255.255.0")   #IH231211 not sure
        self.gateway =  ipaddress.IPv4Address("192.168.1.1")     #IH231211 not sure
        wifi.radio.set_ipv4_address(ipv4=self.ipv4,netmask=self.netmask,gateway=self.gateway)

        #  connect to your SSID
        wifi.radio.connect(self.wifi_ssid, self.wifi_password)

        print("Connected to WiFi")
        pool = socketpool.SocketPool(wifi.radio)
        self.server = Server(pool, "/static", debug=self.debug)

        #  variables for HTML
        #  font for HTML
        self.font_family = "monospace"

        print("starting server..")
        # startup the server
        try:
            self.server.start(str(wifi.radio.ipv4_address))
            print("Listening on http://%s:80" % wifi.radio.ipv4_address)
        #  if the server fails to begin, restart the pico w
        except OSError:
            time.sleep(5)
            print("restarting..")
            microcontroller.reset()
        self.ping_address = ipaddress.ip_address("8.8.4.4")   

        #  text objects for screen
        self.clock = time.monotonic()

        # while True:
        #     try:
        #         #  every 30 seconds, ping server & update temp reading
        #         if (clock + 30) < time.monotonic():
        #             if wifi.radio.ping(ping_address) is None:
        #                 print("lost connection")  # IH231211 observed not be reliable
        #             else:
        #                 print("connected")
        #             clock = time.monotonic()
                    
        #         #  poll the server for incoming/outgoing requests
        #         server.poll()
        #     except Exception as e:
        #         print(e)
        #         continue

    def Poll(self):
        self.sever.poll()

    #  the HTML script
    #  setup as an f string
    #  this way, can insert string variables from code.py directly
    #  of note, use {{ and }} if something from html *actually* needs to be in brackets
    #  i.e. CSS style formatting
    def Webpage(self):
        self.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta http-equiv="Content-type" content="text/html;charset=utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        html{{font-family: {self.font_family}; background-color: lightgrey;
        display:inline-block; margin: 0px auto; text-align: center;}}
        h1{{color: deeppink; width: 200; word-wrap: break-word; padding: 2vh; font-size: 35px;}}
        p{{font-size: 1.5rem; width: 200; word-wrap: break-word;}}
        .button{{font-family: {self.font_family};display: inline-block;
        background-color: black; border: none;
        border-radius: 4px; color: white; padding: 16px 40px;
        text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}}
        p.dotted {{margin: auto;
        width: 75%; font-size: 25px; text-align: center;}}
        </style>
        </head>
        <body>
        <title>Fountain HTTP Server</title>
        <h1>Fountain HTTP Server</h1>
        <br>
        <p class="dotted">This is an HTTP server with CircuitPython.</p>
        <br>
        <h1>Control the LED on the ESP board with these buttons:</h1><br>
        <form accept-charset="utf-8" method="POST">
        <button class="button" name="LED ON" value="ON" type="submit">LED ON</button></a></p></form>
        <p><form accept-charset="utf-8" method="POST">
        <button class="button" name="LED OFF" value="OFF" type="submit">LED OFF</button></a></p></form>
        </body></html>
        """
        return self.html

    #  route default static IP
    @server.route("/")
    def base(request: Request):
        #  serve the HTML f string
        #  with content type text/html
        return Response(request, f"{webpage()}", content_type='text/html')

    #  if a button is pressed on the site
    @server.route("/", POST)
    def buttonpress(request: Request):
        #  get the raw text
        raw_text = request.raw_request.decode("utf8")
        print(raw_text)
        #  if the led on button was pressed
        if "ON" in raw_text:
            #  turn on the onboard LED
            led.value = True
        #  if the led off button was pressed
        if "OFF" in raw_text:
            #  turn the onboard LED off
            led.value = False
        #  reload site
        return Response(request, f"{webpage()}", content_type='text/html')

    print("starting server..")
    # startup the server
    try:
        server.start(str(wifi.radio.ipv4_address))
        print("Listening on http://%s:80" % wifi.radio.ipv4_address)
    #  if the server fails to begin, restart the pico w
    except OSError:
        time.sleep(5)
        print("restarting..")
        microcontroller.reset()
    ping_address = ipaddress.ip_address("8.8.4.4")   

    #  text objects for screen
    clock = time.monotonic()
    while True:
        try:
            #  every 30 seconds, ping server & update temp reading
            if (clock + 30) < time.monotonic():
                if wifi.radio.ping(ping_address) is None:
                    print("lost connection")  # IH231211 observed not be reliable
                else:
                    print("connected")
                clock = time.monotonic()
                
            #  poll the server for incoming/outgoing requests
            server.poll()
        # pylint: disable=broad-except
        except Exception as e:
            print(e)
            continue
