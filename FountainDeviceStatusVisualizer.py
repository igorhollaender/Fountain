#
#    F o u n t a i n   D e v i c e   S t a t u s   V i s u a l i z e r . p y 
#
#    Last revision: IH240219

import time
from boardResources import FountainDeviceCollection
from FountainApplicationData import fountainApp, timeToHMS

class FountainDeviceStatusVisualizer():
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
        self.visualizerPrint(f'Time T+{timeToHMS(time.time()-fountainApp["timeAtStart"])}, {fountainApp["currentStatusString"]}')
        for device in fountainApp["fountainDeviceCollection"].deviceList:
            if device.getNativeFormatID() in [FountainDeviceCollection.LED1]: #IH240219 LED1 (board LED) temporarily used for heartBeat
                self.visualizerPrint (f'{device.getSimpleFormatID()}: not monitored')        
                continue
            self.showDeviceStatus(device)
        self.visualizerFlushPrintBuffer()

    @staticmethod
    def IntensityBarString(percentage) -> str:
        maxBarLength = 50
        return 'I'+'|' * int(percentage/100*maxBarLength)
        
    def showDeviceStatus(self, device):        
        self.visualizerPrint (f'{device.getSimpleFormatID()}: {FountainDeviceStatusVisualizer.IntensityBarString(device.getState('percentageValue'))}')
        # self.visualizerPrint (f'{device.getSimpleFormatID()}: {device.getState('percentageValue')}')
        
        
        