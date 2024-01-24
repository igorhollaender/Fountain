#
#    F o u n t a i n   S i m u l a t e d   R T C . p y 
#
#    Last revision: IH240122
#
#    RTC simulated by HTTP request to a standard site


# see
# https://github.com/adafruit/Adafruit_CircuitPython_Requests/blob/main/examples/requests_https_circuitpython.py


import adafruit_requests as requests
import os
import ssl
import wifi
import socketpool


class FountainSimulatedRTC:
    
    def __init__(
                self, 
                wifi_ssid,
                wifi_password,
                debug=True) -> None:
        
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.debug = debug

        #  connect to your SSID
        wifi.radio.connect(self.wifi_ssid, self.wifi_password)
        self.socket = socketpool.SocketPool(wifi.radio)


        context = ssl.create_default_context()
        context.check_hostname = False
        self.https = requests.Session(self.socket, context)

        UNDEFINED_URL = 'https://httpbin.org/status/undefined'
        UNDEFINED_URL = 'https://httpbin.org/get'
        UNDEFINED_URL = 'https://google.com'

        # IH240123 PROBLEM HERE this does not work (probably a port problem?)
        # gaierror: (-2, 'Name or service not known')
        response = self.https.get(UNDEFINED_URL)
        print("-" * 40)
        print("Text Response: ", response.text)
        print("-" * 40)
        response.close()
        
        

    




