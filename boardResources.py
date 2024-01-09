#
#    b o a r d    R e s o u r c e s  . p y 
#
#    Last revision: IH240108
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

    def __init__(self) -> None:
        # print (fountainSimulated)
        pass
        
    
    # hardware control methods
    
    def pwm_setStatic(device=0, pwm_percentage=100):
        global fountainSimulated
        #IH231219 TODO
        if fountainSimulated:
            print(f"Device {device}: pwm set to {pwm_percentage} percent")
            boardLED.value = (pwm_percentage>50)
            return
        else:
            pass
        pass

    def pwm_setLinearRamp(device=0, pwm_percentage_begin=0, pwm_percentage_end=100, totalDuration=1, numberOfSteps=10):
        """
        Use to schedule pwm setup steps for linear ramp.
        totalDuration    is given in general time units
        numberOfSteps    includes the beginning and end steps
        """
        #IH231219 TODO  
        pass
