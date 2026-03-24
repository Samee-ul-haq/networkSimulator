from src.classes.medium.switch import Switch
from src.classes.station.device import Device


def createSwitchTopology(num_devices=5):
    """
    Creates a star topology with a switch at the center.
    Unlike a hub, the switch learns MAC addresses and does unicast forwarding.
    """
    devicesList = []

    for i in range(num_devices):
        device = Device('PC' + str(i))
        devicesList.append(device)

    sw = Switch(num_devices)

    for device in devicesList:
        port = sw.connect(device)
        device.port = port

    print(f"[TOPO] Switch topology created: {num_devices} devices connected to switch.")
    for d in devicesList:
        print(f"  {d.name}: mac={d.macAddress}, port={d.port}")

    # Broadcast domains: 1 (switch is one broadcast domain)
    # Collision domains : num_devices (each port is its own collision domain)
    print(f"\n[TOPO] Broadcast domains: 1")
    print(f"[TOPO] Collision domains : {num_devices}")

    return sw, devicesList
