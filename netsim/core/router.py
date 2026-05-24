"""
Core — Router (Layer 3 forwarding device).

Extends Node with:
  - A RoutingTable (static routes + RIP-learned routes).
  - forward_packet(): looks up destination, does ARP for next hop,
    builds new Ethernet frame, transmits on outgoing interface.
  - RIP instance for dynamic routing.

The router does NOT pass IP packets to application layer (unless they
are addressed to the router itself, e.g. management traffic).
"""

from core.node              import Node
from datalink.arp           import ARPRequest, ARPReply
from datalink.frame         import EthernetFrame
from network.packet         import IPPacket
from network.routing_table  import RoutingTable
from network.rip            import RIP


class Router(Node):
    def __init__(self, name: str):
        super().__init__(name)
        self.routing_table = RoutingTable(owner_name=name)
        self.rip           = RIP(self)

    # ── Route management ──────────────────────────────────────────────── #

    def add_route(self, route):
        self.routing_table.add_route(route)

    def show_routing_table(self):
        self.routing_table.show()

    # ================================================================== #
    #  RECEIVE  (override Node — router forwards, doesn't consume)        #
    # ================================================================== #

    def receive_frame(self, frame: EthernetFrame, incoming_interface=None):
        RULE = "-" * 60
        print(f"\n{RULE}")
        print(f"[ROUTER {self.name}]  RECEIVED frame")
        print(RULE)

        # ── DATA LINK ─────────────────────────────────────────────────
        print(f"\n  ▲ [DATA LINK — {self.name}]")

        if not frame.verify_fcs():
            print("  [DL] ✗ FCS error — frame dropped!")
            return
        print("  [DL] ✓ FCS valid")

        # ARP handling
        if frame.ethertype == 0x0806:
            iface = incoming_interface or self.interfaces[0]
            p = frame.payload
            if isinstance(p, ARPRequest):
                self.arp_table.handle_arp_request(p, iface)
            elif isinstance(p, ARPReply):
                self.arp_table.handle_arp_reply(p)
            return

        # Accept frame addressed to any of our MACs or broadcast
        my_macs = {iface.mac.upper() for iface in self.interfaces}
        if (frame.dst_mac.upper() not in my_macs and
                frame.dst_mac.upper() != "FF:FF:FF:FF:FF:FF"):
            print(f"  [DL] Not for me (dst={frame.dst_mac}) — dropped")
            return

        frame.show()

        # ── NETWORK ───────────────────────────────────────────────────
        print(f"\n  ▲ [NETWORK — {self.name}]")

        packet = frame.payload
        if not isinstance(packet, IPPacket):
            print("  [NET] Unknown payload — dropped")
            return

        packet.show()

        # Is it addressed to this router?
        my_ips = {iface.ip_addr() for iface in self.interfaces}
        if packet.dst_ip in my_ips:
            print(f"  [NET] Packet is for this router — local delivery")
            return

        # Decrement TTL
        if not packet.decrement_ttl():
            print("  [NET] TTL expired — packet dropped (would send ICMP TTL Exceeded)")
            return
        print(f"  [NET] TTL decremented → {packet.ttl}")

        # Forward
        self.forward_packet(packet)

    # ── Forwarding ────────────────────────────────────────────────────── #

    def forward_packet(self, packet: IPPacket):
        print(f"\n  ► [ROUTER {self.name}] Forwarding → {packet.dst_ip}")

        route = self.routing_table.lookup(packet.dst_ip)
        if route is None:
            print(f"  [NET] No route to {packet.dst_ip} — packet dropped!")
            return
        print(f"  [NET] Route matched: {route}")

        # Find outgoing interface
        out_iface = None
        for iface in self.interfaces:
            if iface.name == route.interface:
                out_iface = iface
                break
        if out_iface is None:
            print(f"  [NET] Interface '{route.interface}' not found!")
            return

        # Determine next-hop IP
        next_hop_ip = packet.dst_ip if route.next_hop == "direct" else route.next_hop

        # ARP resolution for next hop
        print(f"\n  ▼ [DATA LINK — {self.name}]")
        next_hop_mac = self.arp_table.resolve_or_request(next_hop_ip, out_iface)
        if next_hop_mac is None:
            print(f"  [DL] ARP failed for {next_hop_ip} — cannot forward")
            return

        # Build new Ethernet frame (router re-frames the packet)
        frame = EthernetFrame(
            src_mac = out_iface.mac,
            dst_mac = next_hop_mac,
            payload = packet,
        )
        print(f"  [DL] New frame: {out_iface.mac} → {next_hop_mac}")
        frame.show()

        # Transmit
        print(f"\n  ▼ [PHYSICAL — {self.name}]")
        out_iface.transmit(frame)
