#
#    f o u n t a i n   S h o w   S c h e d u l e r . p y 
#
#    Last revision: IH231219
#

import sched
import time
from collections import namedtuple


ScheduledDeviceAction = namedtuple('ScheduledDeviceAction', 'time, device, action, kwargs')

class FountainShowScheduler():

    def __init__(
                self, 
                showSchedule,
                debug=True) -> None:

        self.showSchedule = showSchedule
        self.debug = debug
        self.scheduler = sched.scheduler(timefunc=time)

        self.setSchedule()

    def setSchedule(self):
        self.cleanSchedule()
        pass

    def cleanSchedule(self):
        pass

    def runNonblocking(self):
        pass

    @staticmethod
    def TestSchedule():
        schedule = [
            ScheduledDeviceAction(0,"PUMP1",pwm_setStatic,kwargs={'pwm_percentage': 100})
        ]
        return schedule
