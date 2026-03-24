from src.utils.mac import giveMacAddress
from src.classes.station.physicalLayer import senderSidePhysical,recieverSidePhysical
from src.classes.station.dataLinkLayer import senderSideDataLink,recieverSideDataLink

class Device:
    companyIdentifier='00:1A:2B'
    def __init__(self,name):
        self.name=name
        self.macAddress=giveMacAddress(Device.companyIdentifier)
        self.port=None
        self.senderSidePhysical=senderSidePhysical(self)
        self.recieverSidePhysical=recieverSidePhysical(self)
        self.senderSideDataLink=senderSideDataLink(self)
        self.recieverSidePhysical=recieverSideDataLink(self)

    def send(self, dest_mac, data, medium):
        """
        Public API to send data from this device.
        Triggers the full sender stack: DataLink -> Physical -> Medium
        """
        print(f"\n[DEVICE] {self.name} ({self.macAddress}) sending to {dest_mac}: '{data}'")
        self.senderSideDataLink.send(dest_mac, data, medium)

    def __repr__(self):
        return f"Device(name={self.name}, mac={self.macAddress}, port={self.port})"
