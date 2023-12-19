#
#    b o a r d    R e s o u r c e s  . p y 
#
#    Last revision: IH231219
#
#

import board
from digitalio import DigitalInOut, Direction


# --- general Adafruit board resources

#  onboard LED
boardLED = DigitalInOut(board.LED)
boardLED.direction = Direction.OUTPUT
boardLED.value = False

# --- Fountain specific resources

#IH231219 CircuitPython does not have an enum class
class FountainDevice(simulated=False):
    
    def __init__(self) -> None:
        self.simulated = simulated

        # the ID number of the device also specifies its priority when scheduling actions
        # device with ID 0 is reserved
        self.PUMP1   = 1
        self.PUMP2   = 2
        self.LED1    = 3
        self.LED2    = 4

    
    # hardware control methods
    
    def pwm_setStatic(device=0, pwm_percentage=100):
        #IH231219 TODO
        if self.simulated:
            print(f"Device {device}: pwm set to {pwm_percentage} percent")
            return
        pass

    def pwm_setLinearRamp(device=0, pwm_percentage_begin=0, pwm_percentage_end=100, totalDuration=1, numberOfSteps=10):
        """
        Use to schedule pwm setup steps for linear ramp.
        totalDuration    is gievn in general time units
        numberOfSteps    includes the beginning and end steps
        """
        #IH231219 TODO  
        pass
