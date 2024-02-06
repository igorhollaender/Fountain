#
#    f o u n t a i n   A p p l i c a t i o n   D a t a . p y 
#
#    Last revision: IH240206
#

fountainApp={
       "version": "", # has to be assigned in the main.py
       "currentSchedule": [],
       "fountainDeviceCollection": [],
       "verboseLevel": 1,
       "simulated": True,
}

def debugPrint(debugLevel,s):
    if fountainApp["verboseLevel"]>=debugLevel:
        print(s)
    