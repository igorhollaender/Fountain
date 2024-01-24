#
#    f o u n t a i n   S h o w   S c h e d u l e r . p y 
#
#    Last revision: IH240124
#

import sched
import time
from collections import namedtuple

from boardResources import FountainDevice


ScheduledDeviceAction = namedtuple('ScheduledDeviceAction', 'time device action kwargs')

class FountainShowScheduler():

    def __init__(
                self, 
                showSchedule,
                startDelayMilliSeconds=0,
                debug=True) -> None:

        self.showSchedule = showSchedule
        self.debug = debug
        self.scheduler = sched.scheduler(timefunc=time.monotonic)
        self.startDelayMilliSeconds = startDelayMilliSeconds

        self.scheduledEventList = []
        self.setSchedule(self.showSchedule)
        

        # print(f"FOUNTAIN--> Actual queue: {self.scheduler.queue}")

    def setSchedule(self,schedule):
        self.cleanSchedule()
        for deviceAction in schedule:
            self.scheduledEventList.append(self.scheduler.enter(
                deviceAction.time + self.startDelayMilliSeconds/1000,
                deviceAction.device,  #the device ID number defines priority
                deviceAction.action,
                kwargs=deviceAction.kwargs))

    @staticmethod
    def validateSchedule(schedule) -> bool:
         """
         returns True is the schedule is correctly formed
         """
         #IH240124 TODO implement
         return True  
    
    @staticmethod
    def convertSchedule(schedule):
         """
         converts the schedule from client text format to native format
         """
         #IH240124 TODO implement
         return FountainShowScheduler.TestSchedule() #IH240124 for debugging only
    
    def cleanSchedule(self):
        """
        delete all scheduled events
        """
        for event in self.scheduledEventList:
            try:
                    # event may not be in the sequence
                	self.scheduler.cancel(event)
            except:
                    pass
        self.scheduledEventList=[]

    def empty(self):
        return self.scheduler.empty()

    def runNonblocking(self):
        self.scheduler.run(blocking=False)  


    @staticmethod
    def DefaultSchedule():
        schedule = [
             # setting all devices to idle
            ScheduledDeviceAction(0,FountainDevice.PUMP1,FountainDevice.pwm_setStatic,kwargs={'pwm_percentage': 0}),
        ]
        return schedule
    
    @staticmethod
    def TestSchedule():
        schedule = [
            # device actions with time<0 are used to cleanup after premature sequence finish
            # (the cleanup actions are executed in ascending order, i.e. -3, then -2, then -1. )
            ScheduledDeviceAction(-1,FountainDevice.PUMP1,FountainDevice.pwm_setStatic,kwargs={'pwm_percentage': 0}),
            
            # device action with time=0 is used to initialize the devices

            ScheduledDeviceAction(1.0,FountainDevice.PUMP1,FountainDevice.pwm_setStatic,kwargs={'pwm_percentage': 0}),
            ScheduledDeviceAction(3.0,FountainDevice.PUMP1,FountainDevice.pwm_setStatic,kwargs={'pwm_percentage': 100}),
            ScheduledDeviceAction(5.0,FountainDevice.PUMP1,FountainDevice.pwm_setStatic,kwargs={'pwm_percentage': 0}),
            ScheduledDeviceAction(7.0,FountainDevice.PUMP1,FountainDevice.pwm_setStatic,kwargs={'pwm_percentage': 100}),
            ScheduledDeviceAction(8.0,FountainDevice.PUMP1,FountainDevice.pwm_setStatic,kwargs={'pwm_percentage': 0}),
        ]
        return schedule
