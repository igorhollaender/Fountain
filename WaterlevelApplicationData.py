#
#    W a t e r l e v e l   A p p l i c a t i o n   D a t a . p y 
#
#    Last revision: IH250303
#
import time
from adafruit_httpserver import Websocket

ws : Websocket = None

waterlevelApp={
       "version": "", # has to be assigned in the main.py

       "fountainDeviceCollection": [],
       "verboseLevel": 1,
       "simulated": True,
       "timeAtStart": 0,

       "websocket": ws,
    }

def debugPrint(debugLevel,s):
    if waterlevelApp["verboseLevel"]>=debugLevel:
        print(s)

def timeToHMS(timeSeconds):
    # see https://www.geeksforgeeks.org/python-program-to-convert-seconds-into-hours-minutes-and-seconds/
    min,sec = divmod(timeSeconds,60)
    hour,min = divmod(min,60)
    return '%d:%02d:%02d' % (hour,min,sec)

    