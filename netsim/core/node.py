"""
Core — Node (end device / host).

Implements the full downward (send) and upward (receive) protocol pipeline:

  send_data()
    ├─ [APPLICATION]  caller provides message + ports
    ├─ [TRANSPORT]    wraps data in TCPSegment (checksum)
    ├─ [NETWORK]      wraps segment in IPPacket
    ├─ [DATA LINK]    ARP lookup → EthernetFrame (CRC-32)
    └─ [PHYSICAL]     Interface.transmit() → Channel / Hub / Switch

  receive_frame()
    ├─ [PHYSICAL]     called by Interface.receive()
    ├─ [DATA LINK]    FCS verify → MAC check → ARP dispatch
    ├─ [NETWORK]      extract IPPacket → check dst IP
    ├─ [TRANSPORT]    extract TCPSegment → checksum verify
    └─ [APPLICATION]  dispatch to registered process
"""

from datalink.arp   import ARPTable, ARPRequest, ARPReply
from datalink.frame import EthernetFrame
from network.packet import IPPacket
from transport.segment import TCPSegment


class Node:
    def __init__(self, name: str):
        self.name       = name
        self.interfaces = []
        self.arp_table  = ARPTable(owner=self)
        self.processes  = {}   # port (int) → app_name (str) or callable

    # ── Interface management ──────────────────────────────────────────── #

    def add_interface(self, interface):
        interface.node = self
        self.interfaces.append(interface)

    def get_interface(self, name: str):
        for iface in self.interfaces:
            if iface.name == name:
                return iface
        return None

    def show_interfaces(self):
        print(f"\n  [{self.name}] interfaces:")
        for iface in self.interfaces:
            print(f"    {iface.name}: IP={iface.ip}  MAC={iface.mac}")

    # ── Process / port management ─────────────────────────────────────── #

    def register_process(self, port: int, app_name: str):
        self.processes[port] = app_name
        print(f"[APP] {self.name}: '{app_name}' listening on port {port}")

    # ================================================================== #
    #  SEND  (top-down: App → Transport → Network → DataLink → Physical)  #
    # ================================================================== #

    def send_data(self, destination_ip: str, message,
                  gateway: str,
                  source_port: int, destination_port: int,
                  sequence_number: int = 0):

        RULE = "=" * 60
        print(f"\n{RULE}")
        print(f"[{self.name}]  SENDING  →  {destination_ip}:{destination_port}")
        print(RULE)

        # ── TRANSPORT LAYER ───────────────────────────────────────────
        print(f"\n  ▼ [TRANSPORT LAYER — {self.name}]")
        segment = TCPSegment(
            src_port = source_port,
            dst_port = destination_port,
            seq_num  = sequence_number,
            ack_num  = 0,
            data     = message,
        )
        segment.show()

        # ── NETWORK LAYER ─────────────────────────────────────────────
        print(f"\n  ▼ [NETWORK LAYER — {self.name}]")
        src_ip = self.interfaces[0].ip_addr()
        packet = IPPacket(src_ip=src_ip, dst_ip=destination_ip, payload=segment)
        packet.show()

        # ── DATA LINK LAYER ───────────────────────────────────────────
        print(f"\n  ▼ [DATA LINK LAYER — {self.name}]")
        out_iface    = self.interfaces[0]
        next_hop_ip  = gateway if gateway else destination_ip

        next_hop_mac = self.arp_table.resolve_or_request(next_hop_ip, out_iface)
        if next_hop_mac is None:
            print(f"  [DL] ARP failed for {next_hop_ip} — cannot send")
            return

        frame = EthernetFrame(
            src_mac = out_iface.mac,
            dst_mac = next_hop_mac,
            payload = packet,
        )
        frame.show()

        # ── PHYSICAL LAYER ────────────────────────────────────────────
        print(f"\n  ▼ [PHYSICAL LAYER — {self.name}]")
        out_iface.transmit(frame)

    # ================================================================== #
    #  RECEIVE  (bottom-up: Physical → DataLink → Network → Transport     #
    #            → Application)                                           #
    # ================================================================== #

    def receive_frame(self, frame: EthernetFrame, incoming_interface=None):
        """Entry point: called by Interface.receive()."""

        RULE = "-" * 60
        print(f"\n{RULE}")
        print(f"[{self.name}]  RECEIVED frame")
        print(RULE)

        # ── DATA LINK LAYER ───────────────────────────────────────────
        print(f"\n  ▲ [DATA LINK LAYER — {self.name}]")

        if not frame.verify_fcs():
            print("  [DL] ✗ FCS error — frame dropped!")
            return
        print("  [DL] ✓ FCS valid")

        # ARP frames
        if frame.ethertype == 0x0806:
            iface = incoming_interface or self.interfaces[0]
            payload = frame.payload
            if isinstance(payload, ARPRequest):
                self.arp_table.handle_arp_request(payload, iface)
            elif isinstance(payload, ARPReply):
                self.arp_table.handle_arp_reply(payload)
            return

        # Check destination MAC
        my_macs = {iface.mac.upper() for iface in self.interfaces}
        if (frame.dst_mac.upper() not in my_macs and
                frame.dst_mac.upper() != "FF:FF:FF:FF:FF:FF"):
            print(f"  [DL] Frame not for me (dst={frame.dst_mac}) — dropped")
            return

        frame.show()

        # ── NETWORK LAYER ─────────────────────────────────────────────
        print(f"\n  ▲ [NETWORK LAYER — {self.name}]")

        packet = frame.payload
        if not isinstance(packet, IPPacket):
            print("  [NET] Unknown payload — dropped")
            return

        packet.show()

        my_ips = {iface.ip_addr() for iface in self.interfaces}
        if packet.dst_ip not in my_ips:
            print(f"  [NET] Packet not destined for me ({packet.dst_ip}) — dropped")
            return

        # ── TRANSPORT LAYER ───────────────────────────────────────────
        print(f"\n  ▲ [TRANSPORT LAYER — {self.name}]")

        segment = packet.payload
        if not isinstance(segment, TCPSegment):
            print("  [TRANSPORT] Unknown segment type — dropped")
            return

        segment.show()

        if not segment.verify_checksum():
            print("  [TRANSPORT] ✗ Checksum error — segment dropped!")
            return
        print("  [TRANSPORT] ✓ Checksum valid")

        # ── APPLICATION LAYER ─────────────────────────────────────────
        print(f"\n  ▲ [APPLICATION LAYER — {self.name}]")

        port    = segment.dst_port
        process = self.processes.get(port)

        if process is None:
            print(f"  [APP] No process on port {port} — dropped")
            return

        print(f"  [APP] Delivered to '{process}' (port {port})")
        print(f"  [APP] Data: {segment.data!r}")

        # If process is callable (e.g. app object), invoke it
        if callable(process):
            process(segment.data, packet.src_ip)
