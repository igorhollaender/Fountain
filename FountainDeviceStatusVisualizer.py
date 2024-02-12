#
#    F o u n t a i n   D e v i c e   S t a t u s   V i s u a l i z e r . p y 
#
#    Last revision: IH240208

from boardResources import FountainDeviceCollection

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
        self.visualizerPrint(´\n\n\n')
        for device in FountainDeviceCollection.DeviceSimpleFormat:
            self.showDeviceStatus(device)
        pass

    @staticmethod
    def IntensityBarString(percentage) -> str:
        maxBarLength = 50
        return 'I'+'|' * int(percentage/100*maxBarLength)
        
    def showDeviceStatus(self, device):
        self.visualizerPrint (f'{FountainDeviceCollection.DeviceSimpleFormat[device]}: {FountainDeviceStatusVisualizer.IntensityBarString(device)}')
        
        
        
        