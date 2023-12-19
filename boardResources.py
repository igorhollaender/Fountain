#
#    b o a r d    R e s o u r c e s  . p y 
#
#    Last revision: IH231218
#
#

import board
from digitalio import DigitalInOut, Direction


#  onboard LED
boardLED = DigitalInOut(board.LED)
boardLED.direction = Direction.OUTPUT
boardLED.value = False


