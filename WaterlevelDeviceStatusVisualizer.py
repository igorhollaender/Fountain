#
#    W a t e r l e v e l   D e v i c e   S t a t u s   V i s u a l i z e r . p y 
#
#    Last revision: IH250303

import time
import supervisor
from WaterlevelApplicationData import waterlevelApp, timeToHMS

class WaterlevelDeviceStatusVisualizer():
    """
    Periodical buffered status display in stdout 
    """

    def __init__(
                self,
                visualizeLevel  # 0 is 'no printing'
                ) -> None:
        self.visualizeLevel = visualizeLevel
        self.printBuffer = ""
        self.recentPrintBuffer = ""

    def visualizerPrint(self,s) -> None:
        if self.visualizeLevel>0:
            self.printBuffer += s + '\n'
    
    def visualizerFlushPrintBuffer(self) -> None:
        if self.printBuffer != self.recentPrintBuffer:
            print(self.printBuffer)
        self.recentPrintBuffer = self.printBuffer
        self.printBuffer = ""

    def showStatusAll(self) -> None:
        self.visualizerPrint(f'Time T+{timeToHMS(time.time()-waterlevelApp["timeAtStart"])}, {waterlevelApp["currentStatusString"]} ')
        for device in waterlevelApp["waterlevelDeviceCollection"].deviceList:
            self.showDeviceStatus(device)
        self.visualizerFlushPrintBuffer()

    @staticmethod
    def IntensityBarString(percentage) -> str:
        maxBarLength = 50
        return 'I'+'|' * int(percentage/100*maxBarLength)
        
    def showDeviceStatus(self, device):        
        self.visualizerPrint (f'{device.getSimpleFormatID()}: {WaterlevelDeviceStatusVisualizer.IntensityBarString(device.getState('percentageValue'))}')
     
        
        