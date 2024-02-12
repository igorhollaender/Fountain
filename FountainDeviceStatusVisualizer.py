#
#    F o u n t a i n   D e v i c e   S t a t u s   V i s u a l i z e r . p y 
#
#    Last revision: IH240212

import time
from boardResources import FountainDeviceCollection
from FountainApplicationData import fountainApp, timeToHMS

class FountainDeviceStatusVisualizer():

    def __init__(
                self,
                visualizeLevel  # 0 is 'no printing'
                ) -> None:
        self.visualizeLevel = visualizeLevel

    def visualizerPrint(self,s) -> None:
        if self.visualizeLevel>0:
            print(s)

    def showStatusAll(self) -> None:
        self.visualizerPrint('\n\n\n')
        self.visualizerPrint(f'--- Time T+{timeToHMS(time.time()-fountainApp["timeAtStart"])}')
        for device in fountainApp["fountainDeviceCollection"].deviceList:
            self.showDeviceStatus(device)
        pass

    @staticmethod
    def IntensityBarString(percentage) -> str:
        maxBarLength = 50
        return 'I'+'|' * int(percentage/100*maxBarLength)
        
    def showDeviceStatus(self, device):
        self.visualizerPrint (f'{device.getSimpleFormatID()}: {device.getState('percentageValue')}')
        
        
        
        