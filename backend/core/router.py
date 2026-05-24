from core.node import Node
from utils.ip_utils import longest_prefix_match
from datalink.frame import EthernetFrame
from core.simulator import Simulator

class Router(Node):
    def __init__(self, name):
        super().__init__(name)
        self.routing_table = []
    
    def add_route(self, route):
        self.routing_table.append(route)

    def show_routing_table(self):

        print(f"\nRouting Table : {self.name}")

        for route in self.routing_table:
            print(route)

    def find_route(self, destination_ip):

        return longest_prefix_match(
            destination_ip,
            self.routing_table
        )
    
    def forward_packet(self, packet):

        print(f"\n[ROUTER : {self.name}]")

        print(
            f"Received packet destined for "
            f"{packet.dst_ip}"
        )

        route = self.find_route(packet.dst_ip)

        if route is None:

            print("No route found")
            return

        print(
            f"Route found via "
            f"{route.interface}"
        )

        destination_mac = self.arp_table.resolve(
            packet.dst_ip
        )

        if destination_mac is None:

            print(
                f"ARP lookup failed for "
                f"{packet.dst_ip}"
            )

            return

        outgoing_interface = None

        for interface in self.interfaces:

            if interface.name == route.interface:

                outgoing_interface = interface
                break

        frame = EthernetFrame(
            src_mac=outgoing_interface.mac,
            dst_mac=destination_mac,
            payload=packet
        )

        print("\nEncapsulating packet into frame")

        frame.show()

        print("\nFrame transmitted successfully")

        destination_device = Simulator.find_device_by_ip(
            packet.dst_ip
        )

        if destination_device is None:

            print("Destination host not found")
            return

        destination_device.receive_frame(frame)