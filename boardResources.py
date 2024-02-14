#
#    b o a r d    R e s o u r c e s  . p y 
#
#    Last revision: IH240214
#
#

import board
from digitalio import DigitalInOut, Direction
from FountainApplicationData import fountainApp, debugPrint


# --- diverse

timeResolutionMilliseconds = 50

# --- general Adafruit board resources

#  onboard LED
boardLED = DigitalInOut(board.LED)
boardLED.direction = Direction.OUTPUT
boardLED.value = False

# --- Fountain specific resources

class FountainDevice:

    # device classes
    DEVICE_CLASS_PUMP = 1
    DEVICE_CLASS_LED = 2
    
    def __init__(self,deviceClass,nativeFormatID,simpleFormatID) -> None:
        self.deviceClass = deviceClass,
        self.nativeFormatID = nativeFormatID
        self.simpleFormatID = simpleFormatID
        self.state={
            'percentageValue': 0,
        } 
    
    def setState(self,stateParameter,stateValue):
        self.state[stateParameter]=stateValue

    def getState(self,stateParameter):
        return self.state[stateParameter]
    
    def getSimpleFormatID(self) -> str:
        return self.simpleFormatID

    def getNativeFormatID(self) -> int:
        return self.nativeFormatID
    

    @staticmethod
    def pwm_setConstant(device=1, pwm_percentage=100, getSimpleFormatID=False):
        """
        This method is *static* because it will be used as parameter in the scheduler
        """
        #IH231219 TODO
        if getSimpleFormatID:
            return "CONST"
        if fountainApp["simulated"]:
            debugPrint(2,f"Device {device}: pwm set to {pwm_percentage} percent")
            boardLED.value = (pwm_percentage>50)
            return
        else:
            pass
        fountainApp["fountainDeviceCollection"].getDeviceFromNativeFormatID(device).setState("percentageValue",pwm_percentage)
            

    @staticmethod
    def pwm_setLinearRamp(device=1, pwm_percentage_begin=0, pwm_percentage_end=100, totalDuration=1, numberOfSteps=10, getSimpleFormatID=False):
        """
        Use to schedule pwm setup steps for linear ramp.
        totalDuration    is given in general time units
        numberOfSteps    includes the beginning and end steps
        
        
        This method is *static* because it will be used as parameter in the scheduler
        
        """
        if getSimpleFormatID:
            return "LINRAMP"
        #IH231219 TODO  
        pass

    # hardware control methods
    #IH240126 TODO  implement in a more elegant way
    @staticmethod
    def MethodNativeFormat(method_simpleFormatID):
        for method in [
                FountainDevice.pwm_setConstant,
                FountainDevice.pwm_setLinearRamp]:
            if method(getSimpleFormatID=True)==method_simpleFormatID:
                return method


    
    # def pwm_setConstant(self, pwm_percentage=100, getSimpleFormatID=False):
    #     global fountainSimulated
    #     #IH231219 TODO
    #     if getSimpleFormatID:
    #         return "CONST"
    #     self.setState["percentageValue",pwm_percentage]
    #     if fountainApp["simulated"]:
    #         debugPrint(2,f"Device {self.getSimpleFormatID()}: pwm set to {pwm_percentage} percent")
    #         boardLED.value = (pwm_percentage>50)
    #         return
    #     else:
    #         pass
    #     pass

    # def pwm_setLinearRamp(self, pwm_percentage_begin=0, pwm_percentage_end=100, totalDuration=1, numberOfSteps=10, getSimpleFormatID=False):
    #     """
    #     Use to schedule pwm setup steps for linear ramp.
    #     totalDuration    is given in general time units
    #     numberOfSteps    includes the beginning and end steps
    #     """
    #     if getSimpleFormatID:
    #         return "LINRAMP"
    #     #IH231219 TODO  
    #     pass



# IH240205 TODO implement FountainDevice as a class for a *single device*, then
# implement a collection of devices 

class FountainDeviceCollection():

    # the ID number of the device also specifies its priority when scheduling actions
    # device with ID 0 is reserved

    PUMP1   = 1
    PUMP2   = 2
    LED1    = 3
    LED2    = 4

    def __init__(self) -> None:
        self.deviceList = [
            FountainDevice(FountainDevice.DEVICE_CLASS_PUMP, FountainDeviceCollection.PUMP1,'PUMP1'),
            FountainDevice(FountainDevice.DEVICE_CLASS_PUMP, FountainDeviceCollection.PUMP2,'PUMP2'),
            FountainDevice(FountainDevice.DEVICE_CLASS_LED, FountainDeviceCollection.LED1,'LED1'),
            FountainDevice(FountainDevice.DEVICE_CLASS_LED, FountainDeviceCollection.LED2,'LED2'),
        ]
            
        # set all devices to 'idle' state
        for device in self.deviceList:
            if device.deviceClass == FountainDevice.DEVICE_CLASS_PUMP:
                FountainDevice.pwm_setConstant(device,pwm_percentage=0)
            if device.deviceClass == FountainDevice.DEVICE_CLASS_LED:
                FountainDevice.pwm_setConstant(device,pwm_percentage=0)
        
    def getDeviceFromNativeFormatID(self,deviceNativeFormatID)-> FountainDevice:
        for d in self.deviceList:
            if d.getNativeFormatID()==deviceNativeFormatID:
                return d
    
    def getDeviceFromSimpleFormatID(self,deviceSimpleFormatID)-> FountainDevice:
        for d in self.deviceList:
            if d.getSimpleFormatID()==deviceSimpleFormatID:
                return d
    
    def getSimpleDeviceIDFromNativeDeviceID(self,deviceNativeFormatID) -> str:
        return self.getDeviceFromNativeFormatID(deviceNativeFormatID).getSimpleFormatID()

    def getNativeDeviceIDFromSimpleDeviceID(self,deviceSimpleFormatID) -> int:
        return self.getDeviceFromSimpleFormatID(deviceSimpleFormatID).getNativeFormatID()


    #IH240124 TODO  implement in a more elegant way
    #Ih240207 OBSOLETE
    #DeviceSimpleFormat_OLD = {
    #        PUMP1:"PUMP1",
    #        PUMP2:"PUMP2",
    #        LED1:"LED1",
    #        LED2:"LED2",
    #        }
    
    #IH240126 HACK Dangereous!
    #IH2402207 OBSOLETE
    #def DeviceNativeFormat_OLD(device_str): #inversed DeviceSimpleFormat dictionary
    #    return list(FountainDeviceCollection.DeviceSimpleFormat.keys())[list(FountainDeviceCollection.DeviceSimpleFormat.values()).index(device_str)]
    
    #IH240207 DEPRECATED 
    # TODO to be replaced by getNativeDeviceIDFromSimpleDeviceID
    #def DeviceNativeFormat(self,device_str) -> int:
    #    for d in self.deviceList:
    #        if d.getSimpleFormatID==device_str:
    #            return d.getNativeFormatID()
            
    #IH240207 DEPRECATED 
    # TODO to be replaced by getSimpleDeviceIDFromNativeDeviceID
    #def DeviceSimpleFormat(self,device) -> str:
    #    for d in self.deviceList:
    #        if d.getNativeFormatID()==device:
    #            return d.getSimpleFormatID()
            
   
        
    
    # def pwm_setConstant_NEW(self,device=0, pwm_percentage=100, getSimpleFormatID=False):
    #     return self.deviceList[device].pwm_setConstant(pwm_percentage,getSimpleFormatID)
    
    # def pwm_setLinearRamp_NEW(self,device=0, pwm_percentage_begin=0, pwm_percentage_end=100, totalDuration=1, numberOfSteps=10, getSimpleFormatID=False):
    #     return self.deviceList[device].pwm_setLinearRamp(pwm_percentage_begin, pwm_percentage_end, totalDuration, numberOfSteps, getSimpleFormatID)
    

    # def pwm_setConstant(device=0, pwm_percentage=100, getSimpleFormatID=False):
    #     global fountainSimulated
    #     #IH231219 TODO
    #     if getSimpleFormatID:
    #         return "CONST"
    #     if fountainSimulated:
    #         debugPrint(2,f"Device {device}: pwm set to {pwm_percentage} percent")
    #         boardLED.value = (pwm_percentage>50)
    #         return
    #     else:
    #         pass
    #     pass

    # def pwm_setLinearRamp(device=0, pwm_percentage_begin=0, pwm_percentage_end=100, totalDuration=1, numberOfSteps=10, getSimpleFormatID=False):
    #     """
    #     Use to schedule pwm setup steps for linear ramp.
    #     totalDuration    is given in general time units
    #     numberOfSteps    includes the beginning and end steps
    #     """
    #     if getSimpleFormatID:
    #         return "LINRAMP"
    #     #IH231219 TODO  
    #     pass
