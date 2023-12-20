#
#    f o u n t a i n   S h o w   S c h e d u l e r . p y 
#
#    Last revision: IH231220
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
                debug=True) -> None:

        self.showSchedule = showSchedule
        self.debug = debug
        self.scheduler = sched.scheduler(timefunc=time)

        self.setSchedule(showSchedule)
        print(f"FOUNTAIN--> Actual queue: {self.scheduler.queue}")

    def setSchedule(self,schedule):
        self.cleanSchedule()
        for deviceAction in schedule:
            print(deviceAction)
            self.scheduler.enterabs(
                deviceAction.time,
                deviceAction.device,  #the device ID number defines priority
                deviceAction.action,
                kwargs=deviceAction.kwargs)


    def cleanSchedule(self):
        pass

    def runNonblocking(self):
        self.scheduler.run(blocking=False)  

    @staticmethod
    def TestSchedule():
        schedule = [
            ScheduledDeviceAction(0.0,FountainDevice.PUMP1,FountainDevice.pwm_setStatic,kwargs={'device':FountainDevice.PUMP1, 'pwm_percentage': 100}),
            ScheduledDeviceAction(5.0,FountainDevice.PUMP1,FountainDevice.pwm_setStatic,kwargs={'device':FountainDevice.PUMP1, 'pwm_percentage': 0}),
        ]
        return schedule
