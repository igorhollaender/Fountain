#
#    b o a r d    R e s o u r c e s  . p y 
#
#    Last revision: IH240126
#
#

import board
from digitalio import DigitalInOut, Direction

# --- simulation

fountainSimulated = True

# --- diverse

timeResolutionMilliseconds = 50

# --- general Adafruit board resources

#  onboard LED
boardLED = DigitalInOut(board.LED)
boardLED.direction = Direction.OUTPUT
boardLED.value = False


# --- Fountain specific resources

#IH231219 CircuitPython does not have an enum class
class FountainDevice():

    # the ID number of the device also specifies its priority when scheduling actions
    # device with ID 0 is reserved

    PUMP1   = 1
    PUMP2   = 2
    LED1    = 3
    LED2    = 4

    #IH240124 TODO  implement in a more elegant way
    DeviceSimpleFormat = {
            PUMP1:"PUMP1",
            PUMP2:"PUMP2",
            LED1:"LED1",
            LED2:"LED2",
            }
    #IH240126 HACK Dangereous!
    def DeviceNativeFormat(device_str): #inversed DeviceSimpleFormat dictionary
        return list(FountainDevice.DeviceSimpleFormat.keys())[list(FountainDevice.DeviceSimpleFormat.values()).index(device_str)]
    
    def __init__(self) -> None:
        # print (fountainSimulated)
        pass
        
    # hardware control methods
    #IH240126 TODO  implement in a more elegant way
    def MethodNativeFormat(method_simpleFormatID):
        for method in [
                FountainDevice.pwm_setConstant,
                FountainDevice.pwm_setLinearRamp]:
            if method(getSimpleFormatID=True)==method_simpleFormatID:
                return method

    def pwm_setConstant(device=0, pwm_percentage=100, getSimpleFormatID=False):
        global fountainSimulated
        #IH231219 TODO
        if getSimpleFormatID:
            return "CONST"
        if fountainSimulated:
            print(f"Device {device}: pwm set to {pwm_percentage} percent")
            boardLED.value = (pwm_percentage>50)
            return
        else:
            pass
        pass

    def pwm_setLinearRamp(device=0, pwm_percentage_begin=0, pwm_percentage_end=100, totalDuration=1, numberOfSteps=10, getSimpleFormatID=False):
        """
        Use to schedule pwm setup steps for linear ramp.
        totalDuration    is given in general time units
        numberOfSteps    includes the beginning and end steps
        """
        if getSimpleFormatID:
            return "LINRAMP"
        #IH231219 TODO  
        pass
