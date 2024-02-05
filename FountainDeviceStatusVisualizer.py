#
#    F o u n t a i n   D e v i c e   S t a t u s   V i s u a l i z e r . p y 
#
#    Last revision: IH240205

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
        for device in FountainDeviceCollection.DeviceSimpleFormat:
            show
        pass

    @staticmethod
    def IntensityBarString(percentage) -> str:
        return '|||||||||||||||||||||||||||||||||||||||||||'
        
    def showDeviceStatus(self, device):
        visualizerPrint (f'{FountainDeviceCollection.DeviceSimpleFormat[device]}: {FountainDeviceStatusVisualizer.IntensityBarString(device)}')