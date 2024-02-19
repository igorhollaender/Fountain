#
#    b o a r d    R e s o u r c e s  . p y 
#
#    Last revision: IH240219
#
#

import board
from digitalio import DigitalInOut, Direction
from FountainApplicationData import fountainApp, debugPrint


# --- diverse

timeResolutionMilliseconds = 0

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
        
        if getSimpleFormatID:
            return "CONST"
        fountainApp["fountainDeviceCollection"].getDeviceFromNativeFormatID(device).setState("percentageValue",pwm_percentage)
        if fountainApp["simulated"]:
            debugPrint(2,f"Device {device}: pwm set to {pwm_percentage} percent")
        else:
            #IH231219 TODO
            pass

        #IH240215 for debugging only
        if device==FountainDeviceCollection.LED1:
            boardLED.value = pwm_percentage>50
            

    @staticmethod
    def pwm_setLinearRamp(device=1, pwm_percentage_begin=0, pwm_percentage_end=100, totalDuration=1, numberOfInterimSteps=10, getSimpleFormatID=False):
        """
        Use to schedule pwm setup steps for linear ramp.
        totalDuration    is given in general time units
        numberOfInterimSteps    does NOT include the beginning and end
        
        This method is *static* because it will be used as parameter in the scheduler
        """
        if getSimpleFormatID:
            return "LINRAMP"
        
        for rampStep in range(0,numberOfInterimSteps+1):
            stepDelay = rampStep*totalDuration/(numberOfInterimSteps+1)
            stepValue = pwm_percentage_begin + rampStep*(pwm_percentage_end-pwm_percentage_begin)/(numberOfInterimSteps+1)
            fountainApp["currentShowScheduler"].scheduledEventList.append(
                            fountainApp["currentShowScheduler"].scheduler.enter(
                                delay=stepDelay,
                                priority=1,                        
                                action=FountainDevice.pwm_setConstant,
                                argument=(),
                            kwargs={"device":device,"pwm_percentage":stepValue})
                            )

    @staticmethod
    def pwm_setPulses(device=1, pwm_percentage_low=0, pwm_percentage_high=100, duration_low=1, duration_high=1, numberOfHighPulses=10, getSimpleFormatID=False):
        """
        Use to schedule pwm setup steps for a pulse series.
        
        This method is *static* because it will be used as parameter in the scheduler
        """
        if getSimpleFormatID:
            return "PULSES"
        
        for pulseStep in range(0,numberOfHighPulses):
            raisingEdgeDelay = pulseStep*(duration_high+duration_low)
            fallingEdgeDelay = raisingEdgeDelay+duration_high
            fountainApp["currentShowScheduler"].scheduledEventList.append(
                            fountainApp["currentShowScheduler"].scheduler.enter(
                                delay=raisingEdgeDelay,
                                priority=1,                        
                                action=FountainDevice.pwm_setConstant,
                                argument=(),
                            kwargs={"device":device,"pwm_percentage":pwm_percentage_high})
                            )
            fountainApp["currentShowScheduler"].scheduledEventList.append(
                            fountainApp["currentShowScheduler"].scheduler.enter(
                                delay=fallingEdgeDelay,
                                priority=1,                        
                                action=FountainDevice.pwm_setConstant,
                                argument=(),
                            kwargs={"device":device,"pwm_percentage":pwm_percentage_low})
                            )


    # hardware control methods
    #IH240126 TODO  implement in a more elegant way
    @staticmethod
    def MethodNativeFormat(method_simpleFormatID):
        for method in [
                FountainDevice.pwm_setConstant,
                FountainDevice.pwm_setLinearRamp,
                FountainDevice.pwm_setPulses,
                ]:
            if method(getSimpleFormatID=True)==method_simpleFormatID:
                return method


    


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
