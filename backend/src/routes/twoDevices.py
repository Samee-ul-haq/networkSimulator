from src.classes.medium.cable import Cable
from src.classes.station.device import Device


def createTwoDeviceTopology():
    deviceA = Device('A')
    deviceB = Device('B')
    cable   = Cable()

    deviceA.port = cable.connect(deviceA)
    deviceB.port = cable.connect(deviceB)

    print(f"[TOPO] Two-device topology created.")
    print(f"  {deviceA.name}: mac={deviceA.macAddress}, port={deviceA.port}")
    print(f"  {deviceB.name}: mac={deviceB.macAddress}, port={deviceB.port}")

    return deviceA, deviceB, cable   # FIX: was missing return keyword
