#
#    f o u n t a i n   S h o w   S c h e d u l e r . p y 
#
#    Last revision: IH240214

import sched
import time
from collections import namedtuple

from boardResources import FountainDevice, FountainDeviceCollection
from FountainApplicationData import fountainApp


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
                        'method':deviceAction.method,
                        'kwargs':deviceAction.kwargs}  #IH240213 kwargs also contain "device"
                        )
                else:
                    self.scheduledEventList.append(self.scheduler.enter(
                        delay=deviceAction.time + self.startDelayMilliSeconds/1000,
                        priority=deviceAction.device,  #HACK the device native ID number defines priority                        
                        action=deviceAction.method,
                        argument=(),
                        kwargs=deviceAction.kwargs))
        # print(schedule)
        # print(self.scheduler.queue)
        
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
            if actionInNativeFormat is None:
                return ""
            actionInNativeFormat.kwargs.pop("device",None)   # remove "device" key if it exists      
            actionInSimpleFormat = ""
            actionInSimpleFormat += str(actionInNativeFormat.time) + ','
            actionInSimpleFormat += fountainApp["fountainDeviceCollection"].getSimpleDeviceIDFromNativeDeviceID(actionInNativeFormat.device) + ','
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
            1.0, PUMP1, CONST, {'pwm_percentage': 0}
                is converted to native format
            ScheduledDeviceAction(1.0,FountainDevice.PUMP1,FountainDevice.pwm_setConstant,kwargs={'pwm_percentage': 0, 'device': FountainDevice.PUMP1})

            For full list of device IDs, see boardResources.py.
            For full list of PWM actions, see boardResources.py.

            Lines starting with # are comments and are ignored.
            Empty lines or lines containing only spaces are ignored.
        """

        #IH240126 TODO implement full parser with format error detection
        def convertActionToNative(actionInSimpleFormat: str) -> ScheduledDeviceAction:
            if actionInSimpleFormat.isspace() or len(actionInSimpleFormat)==0 or actionInSimpleFormat.startswith('#'):
                return None
            
            s = actionInSimpleFormat.split(",")
            time_str    = s[0]
            device_str  = s[1]
            method_str  = s[2]
            
            thisDevice = fountainApp["fountainDeviceCollection"].getDeviceFromSimpleFormatID(device_str)
            
            kwargs_extended = eval(','.join(s[3:]))            
            kwargs_extended["device"] =  thisDevice.getNativeFormatID()
            s = ScheduledDeviceAction(
                time=float(time_str),
                device = thisDevice.getNativeFormatID(),
                method = thisDevice.MethodNativeFormat(method_str),
                kwargs = kwargs_extended)
            return s                        
        error="OK"
        try:
            scheduleInNativeFormat = [convertActionToNative(actionInSimpleFormat) for actionInSimpleFormat in scheduleInSimpleFormat.split("\n")]
        except Exception as expt:  # if format invalid 
            print (expt)
            scheduleInNativeFormat = ""
            error="INVALID"        
        print('-------------- SIMPLE -----------------')
        print(scheduleInSimpleFormat)
        print('-------------- NATIVE -----------------')
        print(scheduleInNativeFormat)
        print('--------------  -----------------')
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
        # run actions from the self.cleanupEventList 
        for cleanUpEvent in self.cleanupEventList:
            cleanUpEvent['method'](**cleanUpEvent['kwargs'])

    @staticmethod
    def DefaultSchedule():
        # setting all devices to idle

        # IH240213 TODO review the format to avoid doubled device entry
        schedule = [ScheduledDeviceAction(0,device.getNativeFormatID(),
                                  FountainDevice.pwm_setConstant,                                  
                                  kwargs={'device': device.getNativeFormatID(),
                                          'pwm_percentage': 0}) 
                            for device in fountainApp["fountainDeviceCollection"].deviceList]            
        return schedule
    
    @staticmethod
    def TestSchedule():
        schedule = [
            # device actions with time<0 are used to cleanup after (premature) sequence finish
            # (the sequence of the cleanup actions is not defined)

            # 'None' is allowed in the list

            ScheduledDeviceAction(-1,
                                  FountainDeviceCollection.PUMP1,
                                  FountainDevice.pwm_setConstant,
                                  kwargs={'device': FountainDeviceCollection.PUMP1,
                                          'pwm_percentage': 0}),                                  
            ScheduledDeviceAction(-1,
                                  FountainDeviceCollection.PUMP2,
                                  FountainDevice.pwm_setConstant,
                                  kwargs={'device': FountainDeviceCollection.PUMP2,
                                          'pwm_percentage': 0}),                                  
            ScheduledDeviceAction(-1,
                                  FountainDeviceCollection.LED1,
                                  FountainDevice.pwm_setConstant,
                                  kwargs={'device': FountainDeviceCollection.LED1,
                                          'pwm_percentage': 0}),                                  
            ScheduledDeviceAction(-1,
                                  FountainDeviceCollection.LED2,
                                  FountainDevice.pwm_setConstant,
                                  kwargs={'device': FountainDeviceCollection.LED2,
                                          'pwm_percentage': 0}),                                  
            
            # device action with time=0 is used to initialize the devices

            ScheduledDeviceAction(1.0,
                                  FountainDeviceCollection.PUMP1,
                                  FountainDevice.pwm_setConstant,
                                  kwargs={'device': FountainDeviceCollection.PUMP1,
                                          'pwm_percentage': 100}),
            ScheduledDeviceAction(3.0,
                                  FountainDeviceCollection.PUMP2,
                                  FountainDevice.pwm_setConstant,
                                  kwargs={'device': FountainDeviceCollection.PUMP2,
                                          'pwm_percentage': 100}),
            ScheduledDeviceAction(5.0,
                                  FountainDeviceCollection.PUMP2,
                                  FountainDevice.pwm_setConstant,
                                  kwargs={'device': FountainDeviceCollection.PUMP2,
                                          'pwm_percentage': 0}),                                  
            ScheduledDeviceAction(7.0,
                                  FountainDeviceCollection.PUMP1,
                                  FountainDevice.pwm_setConstant,                                  
                                  kwargs={'device': FountainDeviceCollection.PUMP1,
                                          'pwm_percentage': 0}),                                  
            ScheduledDeviceAction(8.0,
                                  FountainDeviceCollection.PUMP1,
                                  FountainDevice.pwm_setConstant,                                  
                                  kwargs={'device': FountainDeviceCollection.PUMP1,
                                          'pwm_percentage': 50}),                                  
            ScheduledDeviceAction(9.0,
                                  FountainDeviceCollection.LED1,
                                  FountainDevice.pwm_setConstant,                                  
                                  kwargs={'device': FountainDeviceCollection.LED1,
                                          'pwm_percentage': 50}),                  
        ]
        return schedule
