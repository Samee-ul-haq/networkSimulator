from src.routes.twoDevices import createTwoDeviceTopology
from src.routes.star import createStarTopology

# twoDeviceNetwork
def createTwoDeviceNetwork():
    A,B,cable=createTwoDeviceTopology()
    return A,B,cable

def transferDataInTwoDeviceNetwork(sender,cable,data):
    sender.send(cable,data)

# starNetwork
def createStarNetwork():
    hub,devicesList=createStarTopology()
    return hub,devicesList
    
def transferDataInStarNetwork(sender,hub,data):
    sender.send(hub,data)


def createTwoStarNetwork(devices_per_hub=5):
    hub1, hub2, sw, group1, group2 = createTwoStarTopology(devices_per_hub)
    return hub1, hub2, sw, group1, group2


# ── Quick demo ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("TEST 1: Point-to-point transmission")
    print("=" * 60)
    A, B, cable = createTwoDeviceNetwork()
    transferDataInTwoDeviceNetwork(A, B.macAddress, cable, "Hello B!")

    print("\n" + "=" * 60)
    print("TEST 2: Star topology (hub)")
    print("=" * 60)
    hub, devices = createStarNetwork(3)
    transferDataInStarNetwork(devices[0], devices[2].macAddress, hub, "Hi PC2!")

    print("\n" + "=" * 60)
    print("TEST 3: Switch topology")
    print("=" * 60)
    sw, devices = createSwitchNetwork(3)
    transferDataInSwitchNetwork(devices[0], devices[1].macAddress, sw, "Hi via switch!")
