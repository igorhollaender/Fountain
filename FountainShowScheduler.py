#
#    f o u n t a i n   S h o w   S c h e d u l e r . p y 
#
#    Last revision: IH240130

import sched
import time
from collections import namedtuple

from boardResources import FountainDevice


ScheduledDeviceAction = namedtuple('ScheduledDeviceAction', 'time device method kwargs')

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
        self.cleanupEventList = []
        self.setSchedule(self.showSchedule)
        
        # print(f"FOUNTAIN--> Actual queue: {self.scheduler.queue}")

    def setSchedule(self,schedule):
        self.cleanSchedule()
        for deviceAction in schedule:
            if deviceAction is not None:
                if deviceAction.time < 0 :  #this is a cleanup action, time is ignored, the sequence of the cleanup actions is not defined
                    self.cleanupEventList.append({
                        'device': deviceAction.device,  #the device ID number defines priority
                        'method':deviceAction.method,
                        'kwargs':deviceAction.kwargs})
                else:
                    self.scheduledEventList.append(self.scheduler.enter(
                        deviceAction.time + self.startDelayMilliSeconds/1000,
                        deviceAction.device,  #the device ID number defines priority
                        deviceAction.method,
                        kwargs=deviceAction.kwargs))

    @staticmethod
    def validateSchedule(scheduleInSimpleFormat) -> bool:
        """
        returns True is the schedule is correctly formed
        """
        return FountainShowScheduler.convertScheduleToNative(scheduleInSimpleFormat)[1] == 'OK'  
    
    @staticmethod
    def convertScheduleToSimple(scheduleInNativeFormat):
        """
        converts the schedule from native format to simple client text format
        """
        def convertActionToSimple(actionInNativeFormat: ScheduledDeviceAction) -> str:
            actionInSimpleFormat = ""
            actionInSimpleFormat += str(actionInNativeFormat.time) + ','
            actionInSimpleFormat += FountainDevice.DeviceSimpleFormat[actionInNativeFormat.device] + ','
            actionInSimpleFormat += actionInNativeFormat.method(getSimpleFormatID=True) + ','
            actionInSimpleFormat += str(actionInNativeFormat.kwargs) #IH240126 TODO find a more elegant stringifying for this
            
            return actionInSimpleFormat
            
        return "\n".join(map(convertActionToSimple,scheduleInNativeFormat))
    
    @staticmethod
    def convertScheduleToNative(scheduleInSimpleFormat):
        """
         converts the schedule from simple client text format to native format

         EXAMPLES:
                line in simple format
            1.0, PUMP1, CONST, 0
                is converted to native format
            ScheduledDeviceAction(1.0,FountainDevice.PUMP1,FountainDevice.pwm_setConstant,kwargs={'pwm_percentage': 0})

            For full list of device IDs, see boardResources.py.
            For full list of PWM actions, see boardResources.py.

            Lines starting with # are comments and are ignored.
            Empty lines or lines containing only spaces are ignored.
        """

        #IH240126 TODO implement full parser with format error detection
        def convertActionToNative(actionInSimpleFormat: str) -> ScheduledDeviceAction:
            if actionInSimpleFormat.isspace() or len(actionInSimpleFormat)==0 or actionInSimpleFormat.startswith('#'):
                return None
            time_str,device_str,method_str,kwargs_str = actionInSimpleFormat.split(",")
            return ScheduledDeviceAction(
                time=float(time_str),
                device = FountainDevice.DeviceNativeFormat(device_str),
                method = FountainDevice.MethodNativeFormat(method_str),
                kwargs = eval(kwargs_str)
            )
        error="OK"
        try:
            scheduleInNativeFormat = [convertActionToNative(actionInSimpleFormat) for actionInSimpleFormat in scheduleInSimpleFormat.split("\n")]
        except Exception as expt:  # if format invalid 
            print (expt)
            scheduleInNativeFormat = ""
            error="INVALID"
        return scheduleInNativeFormat,error
   

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
        self.cleanupEventList=[]

    def empty(self):
        return self.scheduler.empty()

    def runNonblocking(self):
        self.scheduler.run(blocking=False)  

    def runCleanup(self):
        #IH240130 TODO implement
        # run actions from the self.cleanupEventList 
        pass

    @staticmethod
    def DefaultSchedule():
        schedule = [
             # setting all devices to idle
            ScheduledDeviceAction(0,FountainDevice.PUMP1,FountainDevice.pwm_setConstant,kwargs={'pwm_percentage': 0}),
        ]
        return schedule
    
    @staticmethod
    def TestSchedule():
        schedule = [
            # device actions with time<0 are used to cleanup after premature sequence finish
            # (the sequence of the cleanup actions is not defined)

            # 'None' is allowed in the list

            ScheduledDeviceAction(-1,FountainDevice.PUMP1,FountainDevice.pwm_setConstant,kwargs={'pwm_percentage': 0}),
            
            # device action with time=0 is used to initialize the devices

            ScheduledDeviceAction(1.0,FountainDevice.PUMP1,FountainDevice.pwm_setConstant,kwargs={'pwm_percentage': 0}),
            ScheduledDeviceAction(3.0,FountainDevice.PUMP2,FountainDevice.pwm_setConstant,kwargs={'pwm_percentage': 100}),
            ScheduledDeviceAction(5.0,FountainDevice.PUMP1,FountainDevice.pwm_setConstant,kwargs={'pwm_percentage': 0}),
            ScheduledDeviceAction(7.0,FountainDevice.PUMP2,FountainDevice.pwm_setConstant,kwargs={'pwm_percentage': 100}),
            ScheduledDeviceAction(8.0,FountainDevice.LED1,FountainDevice.pwm_setConstant,kwargs={'pwm_percentage': 0}),
        ]
        return schedule
