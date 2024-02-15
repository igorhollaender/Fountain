#
#    f o u n t a i n   A p p l i c a t i o n   D a t a . p y 
#
#    Last revision: IH240214
#
import time

fountainApp={
       "version": "", # has to be assigned in the main.py
       "currentScheduleNative": [],
       "currentStatusString": "Idle",
       "fountainDeviceCollection": [],
       "verboseLevel": 1,
       "simulated": True,
       "fountainDeviceStatusVisualizer": None,
       "timeAtStart": 0,
    }

def debugPrint(debugLevel,s):
    if fountainApp["verboseLevel"]>=debugLevel:
        print(s)

def timeToHMS(timeSeconds):
    # see https://www.geeksforgeeks.org/python-program-to-convert-seconds-into-hours-minutes-and-seconds/
    min,sec = divmod(timeSeconds,60)
    hour,min = divmod(min,60)
    return '%d:%02d:%02d' % (hour,min,sec)

    