# from src.routes.twoDevices import createTwoDeviceTopology
# from src.routes.star import createStarTopology

# # twoDeviceNetwork
# def createTwoDeviceNetwork():
#     A,B,cable=createTwoDeviceTopology()
#     return A,B,cable

# def transferDataInTwoDeviceNetwork(sender,cable,data):
#     sender.send(cable,data)

# # starNetwork
# def createStarNetwork():
#     hub,devicesList=createStarTopology()
#     return hub,devicesList
    
# def transferDataInStarNetwork(sender,hub,data):
#     sender.send(hub,data)


# def createTwoStarNetwork(devices_per_hub=5):
#     hub1, hub2, sw, group1, group2 = createTwoStarTopology(devices_per_hub)
#     return hub1, hub2, sw, group1, group2


# # ── Quick demo ────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     print("=" * 60)
#     print("TEST 1: Point-to-point transmission")
#     print("=" * 60)
#     A, B, cable = createTwoDeviceNetwork()
#     transferDataInTwoDeviceNetwork(A, B.macAddress, cable, "Hello B!")

#     print("\n" + "=" * 60)
#     print("TEST 2: Star topology (hub)")
#     print("=" * 60)
#     hub, devices = createStarNetwork(3)
#     transferDataInStarNetwork(devices[0], devices[2].macAddress, hub, "Hi PC2!")

#     print("\n" + "=" * 60)
#     print("TEST 3: Switch topology")
#     print("=" * 60)
#     sw, devices = createSwitchNetwork(3)
#     transferDataInSwitchNetwork(devices[0], devices[1].macAddress, sw, "Hi via switch!")




# from core.node import Node
# from core.router import Router
# from core.interface import Interface

# pc1 = Node("PC1")

# iface1 = Interface(
#     "eth0",
#     "192.168.1.2/24",
#     "AA:BB:CC:DD:EE:01"
# )

# pc1.add_interface(iface1)

# router = Router("R1")

# iface2 = Interface(
#     "eth0",
#     "192.168.1.1/24",
#     "AA:BB:CC:DD:EE:FF"
# )

# router.add_interface(iface2)

# pc1.show_interfaces()
# router.show_interfaces()

from utils.ip_utils import get_network
from utils.ip_utils import same_subnet

print(get_network("192.168.1.10/24"))

print(
    same_subnet(
        "192.168.1.10/24",
        "192.168.1.20/24"
    )
)