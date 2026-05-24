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

# from utils.ip_utils import get_network
# from utils.ip_utils import same_subnet

# print(get_network("192.168.1.10/24"))

# print(
#     same_subnet(
#         "192.168.1.10/24",
#         "192.168.1.20/24"
#     )
# )

from core.node import Node
from core.router import Router
from core.interface import Interface
from core.simulator import Simulator


from network.packet import IPPacket
from network.routing_table import Route




# =========================
# CREATE DEVICES
# =========================

pc1 = Node("PC1")

router = Router("R1")

pc2 = Node("PC2")

# =========================
# ADD INTERFACES
# =========================

pc1.add_interface(
    Interface(
        "eth0",
        "192.168.1.2/24",
        "AA:AA:AA:AA:AA:01"
    )
)

router.add_interface(
    Interface(
        "eth0",
        "192.168.1.1/24",
        "BB:BB:BB:BB:BB:01"
    )
)

router.add_interface(
    Interface(
        "eth1",
        "10.0.0.1/24",
        "BB:BB:BB:BB:BB:02"
    )
)

pc2.add_interface(
    Interface(
        "eth0",
        "10.0.0.2/24",
        "CC:CC:CC:CC:CC:01"
    )
)


# =========================
# ADD ROUTES
# =========================

router.add_route(
    Route(
        network="10.0.0.0",
        mask="24",
        next_hop="direct",
        interface="eth1"
    )
)

router.add_route(
    Route(
        network="192.168.1.0",
        mask="24",
        next_hop="direct",
        interface="eth0"
    )
)


# PC1 knows router MAC

pc1.arp_table.add_entry(
    "192.168.1.1",
    "BB:BB:BB:BB:BB:01"
)

# Router knows PC2 MAC

router.arp_table.add_entry(
    "10.0.0.2",
    "CC:CC:CC:CC:CC:01"
)


Simulator.add_device(pc1)
Simulator.add_device(router)
Simulator.add_device(pc2)


# =========================
# SHOW ROUTING TABLE
# =========================

router.show_routing_table()


# =========================
# CREATE PACKET
# =========================

packet = IPPacket(
    src_ip="192.168.1.2",
    dst_ip="10.0.0.2",
    payload="Hello PC2"
)

# =========================
# ARP ENTRIES
# =========================

router.arp_table.add_entry(
    "10.0.0.2",
    "CC:CC:CC:CC:CC:01"
)


# =========================
# FORWARD PACKET
# =========================
router.arp_table.show_table()

pc1.send_data(
    destination_ip="10.0.0.2",
    message="Hello PC2",
    gateway="192.168.1.1"
)