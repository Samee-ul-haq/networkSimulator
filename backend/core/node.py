from core.interface import Interface
from datalink.arp import ARPTable
from network.packet import IPPacket
from datalink.frame import EthernetFrame
from core.simulator import Simulator

class Node:
    def __init__(self, name):
        self.name = name
        self.interfaces = []
        self.arp_table = ARPTable()


    def add_interface(self, interface):
        self.interfaces.append(interface)


    def show_interfaces(self):
        print(f"\nInterfaces : {self.name}")

        for i in self.interfaces:
            print(
                f"{i.name} | "
                f"IP={i.ip} | "
                f"MAC={i.mac}"
            )


    def receive_frame(self, frame):
        print(f"\n[{self.name}] received frame")
        frame.show()
        packet = frame.payload

        print(
            f"\n[{self.name}] extracted IP packet"
        )

        print(
            f"Message received : "
            f"{packet.payload}"
        )

    
    def send_data(self,
                  destination_ip,
                  message,
                  gateway):

        print(f"\n[{self.name}]")

        print(
            f"Sending message to "
            f"{destination_ip}"
        )


        # ======================
        # NETWORK LAYER
        # ======================

        packet = IPPacket(
            src_ip=self.interfaces[0].ip.split("/")[0],
            dst_ip=destination_ip,
            payload=message
        )

        print("\n[NETWORK LAYER]")

        print("IP Packet created")


        # ======================
        # ARP LOOKUP
        # ======================

        gateway_mac = self.arp_table.resolve(
            gateway
        )

        if gateway_mac is None:

            print(
                f"ARP lookup failed for "
                f"{gateway}"
            )

            return


        # ======================
        # DATA LINK LAYER
        # ======================

        frame = EthernetFrame(
            src_mac=self.interfaces[0].mac,
            dst_mac=gateway_mac,
            payload=packet
        )

        print("\n[DATA LINK LAYER]")

        print("Ethernet frame created")

        frame.show()


        # ======================
        # SEND TO ROUTER
        # ======================

        router = Simulator.find_device_by_ip(
            gateway
        )

        if router is None:

            print("Gateway not found")
            return

        print("\nFrame transmitted")

        router.forward_packet(packet)