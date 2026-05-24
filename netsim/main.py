"""
Network Simulator — Complete Test Suite
=======================================
Submission 1 : Physical + Data Link Layer
Submission 2 : Network Layer
Submission 3 : Transport + Application Layer

All layers operate in a single integrated pipeline.
Every test logs each layer's activity as the frame travels up or down
the stack — no menu, no artificial separation.

Run:
    cd backend
    python main.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Core ──────────────────────────────────────────────────────────────────
from core.interface  import Interface
from core.node       import Node
from core.router     import Router
from core.simulator  import Simulator

# ── Physical ──────────────────────────────────────────────────────────────
from physical.channel import Channel
from physical.hub     import Hub
from physical.switch  import Switch

# ── Data Link ─────────────────────────────────────────────────────────────
from datalink.frame  import EthernetFrame

# ── Network ───────────────────────────────────────────────────────────────
from network.routing_table import Route, RoutingTable
from network.rip           import RIP

# ── Transport ─────────────────────────────────────────────────────────────
from transport.port_manager import PortManager
from transport.segment      import TCPSegment
from transport.gobackn      import GoBackNSender, GoBackNReceiver

# ── Application ───────────────────────────────────────────────────────────
from application.chat          import ChatApp
from application.file_transfer import FileTransferApp


# ══════════════════════════════════════════════════════════════════════════ #
#  Helpers                                                                   #
# ══════════════════════════════════════════════════════════════════════════ #

def header(title: str):
    bar = "═" * 70
    print(f"\n\n{bar}")
    print(f"  {title}")
    print(bar)


def report_domains(topology: str,
                   collision_domains: int,
                   broadcast_domains: int):
    print(f"\n  ┌── Domain Analysis [{topology}] ───────────────")
    print(f"  │  Collision domains : {collision_domains}")
    print(f"  │  Broadcast domains : {broadcast_domains}")
    print(f"  └──────────────────────────────────────────────")


# ══════════════════════════════════════════════════════════════════════════ #
#  SUBMISSION 1  ·  Physical Layer                                           #
# ══════════════════════════════════════════════════════════════════════════ #

def test_s1_p2p():
    """
    S1-TC1 : Two end-devices connected by a dedicated point-to-point link.
    Demonstrates: physical channel, DL frame, CRC, MAC check, delivery.
    """
    header("S1-TC1 · P2P Direct Link  (2 devices)")

    Simulator.reset()
    PortManager.reset()

    pc1 = Node("PC1")
    pc2 = Node("PC2")

    iface1 = Interface("eth0", "192.168.1.1/24", "AA:AA:AA:AA:AA:01")
    iface2 = Interface("eth0", "192.168.1.2/24", "BB:BB:BB:BB:BB:01")

    pc1.add_interface(iface1)
    pc2.add_interface(iface2)

    # Point-to-point physical channel
    Channel("pc1-pc2").connect(iface1, iface2)

    pc2.register_process(PortManager.WELL_KNOWN_PORTS["CHAT"], "Echo Service")

    # Static ARP entry (same subnet, both sides know each other)
    pc1.arp_table.add_entry("192.168.1.2", "BB:BB:BB:BB:BB:01")

    Simulator.add_device(pc1)
    Simulator.add_device(pc2)

    pc1.send_data(
        destination_ip   = "192.168.1.2",
        message          = "Hello PC2 — P2P link!",
        gateway          = "192.168.1.2",     # same subnet, no router
        source_port      = PortManager.allocate_ephemeral_port(),
        destination_port = PortManager.WELL_KNOWN_PORTS["CHAT"],
    )


def test_s1_hub_star():
    """
    S1-TC2 : Star topology — 5 end-devices connected to a Hub.
    Demonstrates: hub broadcast, CSMA/CD, all devices receive frame,
                  only the addressed device accepts it.
    Domain count: 1 collision domain, 1 broadcast domain.
    """
    header("S1-TC2 · Hub Star Topology  (5 devices + 1 hub)")

    Simulator.reset()
    PortManager.reset()

    hub = Hub("HUB1", num_ports=5)
    devices = []

    for i in range(1, 6):
        pc    = Node(f"PC{i}")
        iface = Interface("eth0",
                          f"192.168.1.{i}/24",
                          f"AA:AA:AA:AA:AA:0{i}")
        pc.add_interface(iface)
        hub.connect(iface)
        pc.register_process(PortManager.WELL_KNOWN_PORTS["CHAT"], "Echo")
        # Pre-populate ARP for all peers
        for j in range(1, 6):
            if j != i:
                pc.arp_table.add_entry(f"192.168.1.{j}",
                                       f"AA:AA:AA:AA:AA:0{j}")
        devices.append(pc)
        Simulator.add_device(pc)

    print("\n[TEST] PC1 → PC4 via hub  (hub will broadcast to all 4 others)")
    devices[0].send_data(
        destination_ip   = "192.168.1.4",
        message          = "Hello PC4 from PC1 via hub!",
        gateway          = "192.168.1.4",
        source_port      = PortManager.allocate_ephemeral_port(),
        destination_port = PortManager.WELL_KNOWN_PORTS["CHAT"],
    )

    report_domains("5 devices + Hub",
                   collision_domains = hub.collision_domains,
                   broadcast_domains = hub.broadcast_domains)


def test_s1_switch():
    """
    S1-TC3 : Switch topology — 5 end-devices connected to a Switch.
    Demonstrates: MAC address learning, selective forwarding, flooding
                  on first transmission (unknown dst), unicast on second.
    Domain count: 5 collision domains (one per port), 1 broadcast domain.
    """
    header("S1-TC3 · Switch Topology  (5 devices + 1 switch)")

    Simulator.reset()
    PortManager.reset()

    sw      = Switch("SW1", num_ports=5)
    devices = []

    for i in range(1, 6):
        pc    = Node(f"PC{i}")
        iface = Interface("eth0",
                          f"10.0.0.{i}/24",
                          f"CC:CC:CC:CC:CC:0{i}")
        pc.add_interface(iface)
        sw.connect(iface)
        pc.register_process(PortManager.WELL_KNOWN_PORTS["CHAT"], "Echo")
        for j in range(1, 6):
            if j != i:
                pc.arp_table.add_entry(f"10.0.0.{j}",
                                       f"CC:CC:CC:CC:CC:0{j}")
        devices.append(pc)
        Simulator.add_device(pc)

    print("\n[TEST] PC1 → PC2  (first time: switch floods because dst unknown)")
    devices[0].send_data(
        destination_ip   = "10.0.0.2",
        message          = "Hello PC2! (flood)",
        gateway          = "10.0.0.2",
        source_port      = PortManager.allocate_ephemeral_port(),
        destination_port = PortManager.WELL_KNOWN_PORTS["CHAT"],
    )

    sw.show_mac_table()

    print("\n[TEST] PC3 → PC1  (switch now knows PC1's port — unicast)")
    devices[2].send_data(
        destination_ip   = "10.0.0.1",
        message          = "Hello PC1 from PC3! (unicast)",
        gateway          = "10.0.0.1",
        source_port      = PortManager.allocate_ephemeral_port(),
        destination_port = PortManager.WELL_KNOWN_PORTS["CHAT"],
    )

    sw.show_mac_table()

    report_domains("5 devices + Switch",
                   collision_domains = sw.collision_domains,
                   broadcast_domains = sw.broadcast_domains)
    
    print("\n[TEST] Flow Control Demonstration (Go-Back-N over Switch)")
    print("       PC1 sending a stream of frames to PC2 with window_size=3")
    
    # 1. Create a sequence of segments/frames to send
    segments = [
        TCPSegment(
            src_port = PortManager.allocate_ephemeral_port(),
            dst_port = PortManager.WELL_KNOWN_PORTS["CHAT"],
            seq_num  = i,
            ack_num  = 0,
            data     = f"L2_FLOW_FRAME_{i}",
        )
        for i in range(5)
    ]

    # 2. Instantiate your existing Go-Back-N protocol
    gbn_sender   = GoBackNSender(window_size=3)
    gbn_receiver = GoBackNReceiver()

    # 3. Execute the transmission (simulating a dropped packet at index 2 to prove it works)
    # The console will log the window sliding and the retransmission.
    gbn_sender.send(segments, gbn_receiver, simulate_loss_at=2)


def test_s1_two_stars():
    """
    S1-TC4 : Two hub-stars (5 PCs each) joined by a switch.
    Demonstrates: inter-segment forwarding, hub CSMA/CD inside each
                  segment, switch MAC learning across both hubs.
    Domain count: 2 collision domains (one per hub), 1 broadcast domain.
    """
    header("S1-TC4 · Two Hub-Stars Connected by Switch  (10 devices)")

    Simulator.reset()
    PortManager.reset()

    hub1 = Hub("HUB1", num_ports=5)
    hub2 = Hub("HUB2", num_ports=5)
    sw   = Switch("SW1", num_ports=2)

    # Hub1 → switch uplink
    hub1.set_uplink(sw)
    hub2.set_uplink(sw)

    # Group 1: 192.168.1.x  (PC1–PC5)
    group1 = []
    for i in range(1, 6):
        pc    = Node(f"PC{i}")
        iface = Interface("eth0",
                          f"192.168.1.{i}/24",
                          f"AA:AA:AA:AA:AA:0{i}")
        pc.add_interface(iface)
        hub1.connect(iface)
        pc.register_process(PortManager.WELL_KNOWN_PORTS["CHAT"], "Echo")
        for j in range(1, 6):
            if j != i:
                pc.arp_table.add_entry(f"192.168.1.{j}",
                                       f"AA:AA:AA:AA:AA:0{j}")
        group1.append(pc)
        Simulator.add_device(pc)

    # Group 2: 192.168.1.x  (PC6–PC10, same /24 subnet via a router in real
    # networks — but the assignment asks us to show hub-to-hub via switch,
    # so we keep them in one broadcast domain as the topology implies)
    group2 = []
    for i in range(6, 11):
        pc    = Node(f"PC{i}")
        mac   = f"BB:BB:BB:BB:BB:0{i - 5}"
        iface = Interface("eth0",
                          f"192.168.1.{i}/24",
                          mac)
        pc.add_interface(iface)
        hub2.connect(iface)
        pc.register_process(PortManager.WELL_KNOWN_PORTS["CHAT"], "Echo")
        group2.append(pc)
        Simulator.add_device(pc)

    # Pre-populate ARP within each group and for cross-group targets
    for pc in group1:
        pc.arp_table.add_entry("192.168.1.6",  "BB:BB:BB:BB:BB:01")
    for pc in group2:
        pc.arp_table.add_entry("192.168.1.1",  "AA:AA:AA:AA:AA:01")

    print("\n[TEST] PC1 (Hub1) → PC3 (Hub1)  [intra-hub]")
    group1[0].send_data(
        destination_ip   = "192.168.1.3",
        message          = "Intra-hub: PC1 to PC3",
        gateway          = "192.168.1.3",
        source_port      = PortManager.allocate_ephemeral_port(),
        destination_port = PortManager.WELL_KNOWN_PORTS["CHAT"],
    )

    print("\n[TEST] PC1 (Hub1) → PC6 (Hub2)  [inter-hub via switch]")
    group1[0].send_data(
        destination_ip   = "192.168.1.6",
        message          = "Inter-hub: PC1 to PC6",
        gateway          = "192.168.1.6",
        source_port      = PortManager.allocate_ephemeral_port(),
        destination_port = PortManager.WELL_KNOWN_PORTS["CHAT"],
    )

    sw.show_mac_table()

    report_domains(
        "10 devices: 2 Hub-stars + 1 Switch",
        collision_domains = hub1.collision_domains + hub2.collision_domains,
        broadcast_domains = 1,
    )
    print("  (Each hub = 1 collision domain. Switch does not break "
          "broadcast domain.)")


# ══════════════════════════════════════════════════════════════════════════ #
#  SUBMISSION 2  ·  Network Layer                                            #
# ══════════════════════════════════════════════════════════════════════════ #

def test_s2_arp_static_routing():
    """
    S2-TC1 : ARP resolution + Static routing.
    Topology : PC1 ─── R1 ─── PC2
               192.168.1.x       10.0.0.x
    PC1 does NOT have R1's MAC pre-cached — ARP is resolved dynamically.
    Router uses longest-prefix-match static table to forward to PC2.
    """
    header("S2-TC1 · Dynamic ARP + Static Routing")

    Simulator.reset()
    PortManager.reset()

    pc1    = Node("PC1")
    router = Router("R1")
    pc2    = Node("PC2")

    # Interfaces
    pc1_eth0 = Interface("eth0", "192.168.1.2/24", "AA:BB:CC:DD:EE:01")
    r1_eth0  = Interface("eth0", "192.168.1.1/24", "AA:BB:CC:DD:EE:02")
    r1_eth1  = Interface("eth1", "10.0.0.1/24",   "AA:BB:CC:DD:EE:03")
    pc2_eth0 = Interface("eth0", "10.0.0.2/24",   "AA:BB:CC:DD:EE:04")

    pc1.add_interface(pc1_eth0)
    router.add_interface(r1_eth0)
    router.add_interface(r1_eth1)
    pc2.add_interface(pc2_eth0)

    # Physical links
    Channel("pc1-r1").connect(pc1_eth0, r1_eth0)
    Channel("r1-pc2").connect(r1_eth1, pc2_eth0)

    # Static routes on router
    router.add_route(Route("192.168.1.0", "24", "direct", "eth0"))
    router.add_route(Route("10.0.0.0",    "24", "direct", "eth1"))

    # Default gateway on PC1 (no ARP pre-cache — will be resolved dynamically)
    # Router knows PC2's MAC pre-cached (simulates prior ARP)
    router.arp_table.add_entry("10.0.0.2", "AA:BB:CC:DD:EE:04")

    pc2.register_process(PortManager.WELL_KNOWN_PORTS["CHAT"], "Chat Service")

    Simulator.add_device(pc1)
    Simulator.add_device(router)
    Simulator.add_device(pc2)

    router.show_routing_table()

    print("\n[TEST] PC1 → PC2 via R1  (ARP for R1 resolved dynamically)")
    pc1.send_data(
        destination_ip   = "10.0.0.2",
        message          = "Hello PC2, routed via R1!",
        gateway          = "192.168.1.1",       # PC1's default gateway
        source_port      = PortManager.allocate_ephemeral_port(),
        destination_port = PortManager.WELL_KNOWN_PORTS["CHAT"],
    )

    print("\n[ARP tables after exchange]")
    pc1.arp_table.show()
    router.arp_table.show()


def test_s2_rip():
    """
    S2-TC2 : RIP dynamic routing (Distance-Vector / Bellman-Ford).
    Topology : PC1 ─── R1 ─── R2 ─── PC2
               192.168.1.x  10.0.0.x  172.16.0.x
    R1 initially knows only its directly connected subnets.
    R2 initially knows only its directly connected subnets.
    After RIP convergence, R1 learns about 172.16.0.0/24 and vice-versa.
    """
    header("S2-TC2 · RIP Dynamic Routing  (2 routers)")

    r1 = Router("R1")
    r2 = Router("R2")

    r1.add_interface(Interface("eth0", "192.168.1.1/24", "R1:E0"))
    r1.add_interface(Interface("eth1", "10.0.0.1/24",   "R1:E1"))

    r2.add_interface(Interface("eth0", "10.0.0.2/24",   "R2:E0"))
    r2.add_interface(Interface("eth1", "172.16.0.1/24", "R2:E1"))

    # Directly connected routes (metric=1)
    r1.add_route(Route("192.168.1.0", "24", "direct", "eth0", metric=1))
    r1.add_route(Route("10.0.0.0",    "24", "direct", "eth1", metric=1))

    r2.add_route(Route("10.0.0.0",    "24", "direct", "eth0", metric=1))
    r2.add_route(Route("172.16.0.0",  "24", "direct", "eth1", metric=1))

    # RIP neighbour relationships
    r1.rip.add_neighbor(r2, local_interface="eth1", next_hop_ip="10.0.0.2")
    r2.rip.add_neighbor(r1, local_interface="eth0", next_hop_ip="10.0.0.1")

    print("\n[RIP] Routing tables BEFORE convergence:")
    r1.routing_table.show()
    r2.routing_table.show()

    # Run RIP
    RIP.converge([r1, r2])

    # Verify
    route_to_172 = r1.routing_table.lookup("172.16.0.2")
    route_to_192 = r2.routing_table.lookup("192.168.1.5")

    print("\n[RIP] Verification:")
    print(f"  R1 → 172.16.0.2 : "
          f"{route_to_172 if route_to_172 else 'NO ROUTE (convergence failed!)'}")
    print(f"  R2 → 192.168.1.5: "
          f"{route_to_192 if route_to_192 else 'NO ROUTE (convergence failed!)'}")


# ══════════════════════════════════════════════════════════════════════════ #
#  SUBMISSION 3  ·  Transport + Application Layer                            #
# ══════════════════════════════════════════════════════════════════════════ #

def _build_routed_topology():
    """
    Shared helper for S3 tests.
    Topology : PC1 ─(eth)─ R1 ─(eth)─ PC2
    Returns  : (pc1, router, pc2)
    """
    Simulator.reset()
    PortManager.reset()

    pc1    = Node("PC1")
    router = Router("R1")
    pc2    = Node("PC2")

    pc1_eth  = Interface("eth0", "192.168.1.2/24", "11:22:33:44:55:01")
    r1_eth0  = Interface("eth0", "192.168.1.1/24", "11:22:33:44:55:02")
    r1_eth1  = Interface("eth1", "10.0.0.1/24",   "11:22:33:44:55:03")
    pc2_eth  = Interface("eth0", "10.0.0.2/24",   "11:22:33:44:55:04")

    pc1.add_interface(pc1_eth)
    router.add_interface(r1_eth0)
    router.add_interface(r1_eth1)
    pc2.add_interface(pc2_eth)

    Channel("pc1-r1").connect(pc1_eth, r1_eth0)
    Channel("r1-pc2").connect(r1_eth1, pc2_eth)

    router.add_route(Route("192.168.1.0", "24", "direct", "eth0"))
    router.add_route(Route("10.0.0.0",    "24", "direct", "eth1"))

    # ARP pre-cached for clean output (dynamic ARP shown in S2-TC1)
    pc1.arp_table.add_entry("192.168.1.1", "11:22:33:44:55:02")
    router.arp_table.add_entry("10.0.0.2",  "11:22:33:44:55:04")

    Simulator.add_device(pc1)
    Simulator.add_device(router)
    Simulator.add_device(pc2)

    return pc1, router, pc2


def test_s3_chat():
    """
    S3-TC1 : Chat application over full protocol stack.
    Demonstrates complete encapsulation:
      ChatApp → TCPSegment → IPPacket → EthernetFrame → wire → Router
      → EthernetFrame → IPPacket → TCPSegment → ChatApp.
    """
    header("S3-TC1 · Chat Application  (Full Protocol Stack)")

    pc1, router, pc2 = _build_routed_topology()

    chat_pc2 = ChatApp(pc2)   # registers on port 5000

    print("\n[TEST] PC1 sends chat message to PC2 via R1")
    pc1.send_data(
        destination_ip   = "10.0.0.2",
        message          = "Hey PC2! Full stack chat message.",
        gateway          = "192.168.1.1",
        source_port      = PortManager.allocate_ephemeral_port(),
        destination_port = ChatApp.PORT,
    )

    print("\n[TEST] Sending a second message")
    pc1.send_data(
        destination_ip   = "10.0.0.2",
        message          = "Second message — same session.",
        gateway          = "192.168.1.1",
        source_port      = PortManager.allocate_ephemeral_port(),
        destination_port = ChatApp.PORT,
    )


def test_s3_file_transfer():
    """
    S3-TC2 : File Transfer with Go-Back-N at transport layer.
    Demonstrates:
      - File split into chunks (Application layer)
      - Each chunk wrapped in a TCP Segment (Transport layer, with checksum)
      - Go-Back-N sliding window with simulated packet loss + retransmission
      - Reassembly at receiver
    """
    header("S3-TC2 · File Transfer  (Go-Back-N, window=4, loss at seq 2)")

    ftp = FileTransferApp(chunk_size=8)
    ftp.send_file(
        data             = "NETWORK_SIMULATOR_COMPLETE_FILE_TRANSFER_DEMONSTRATION",
        window_size      = 4,
        simulate_loss_at = 2,
    )


def test_s3_gobackn_detailed():
    """
    S3-TC3 : Go-Back-N protocol detailed walkthrough.
    8 segments, window=3, loss at seq 4.
    Shows: window sliding, loss detection, retransmission from base,
           cumulative ACKs, final reassembly.
    """
    header("S3-TC3 · Go-Back-N Detail  (8 segments, window=3, loss at seq 4)")

    segments = [
        TCPSegment(
            src_port = 49200,
            dst_port = PortManager.WELL_KNOWN_PORTS["FILE_TRANSFER"],
            seq_num  = i,
            ack_num  = 0,
            data     = f"PKT_{i:02d}",
        )
        for i in range(8)
    ]

    sender   = GoBackNSender(window_size=3)
    receiver = GoBackNReceiver()

    result = sender.send(segments, receiver, simulate_loss_at=4)

    print(f"\n[GBN] Received chunks in order:")
    for i, chunk in enumerate(result):
        print(f"  [{i}] {chunk}")

    reassembled = "".join(str(c) for c in result)
    print(f"\n[GBN] Reassembled : {reassembled!r}")


def test_s3_full_stack_encapsulation():
    """
    S3-TC4 : Explicit end-to-end encapsulation demonstration.
    Shows how data is wrapped at each layer on the way down,
    then unwrapped at each layer on the way up.
    """
    header("S3-TC4 · Full Stack Encapsulation  (App → TCP → IP → Eth → wire)")

    pc1, router, pc2 = _build_routed_topology()
    pc2.register_process(PortManager.WELL_KNOWN_PORTS["FILE_TRANSFER"],
                         "File Transfer Service")

    ftp_data   = "ENCAPSULATION_DEMO"
    print(f"\n[APP] Original data  : {ftp_data!r}")
    print("[APP] ↓ Application layer hands data to Transport")

    pc1.send_data(
        destination_ip   = "10.0.0.2",
        message          = ftp_data,
        gateway          = "192.168.1.1",
        source_port      = PortManager.allocate_ephemeral_port(),
        destination_port = PortManager.WELL_KNOWN_PORTS["FILE_TRANSFER"],
        sequence_number  = 0,
    )


# ══════════════════════════════════════════════════════════════════════════ #
#  Entry point                                                               #
# ══════════════════════════════════════════════════════════════════════════ #

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║       NETWORK SIMULATOR  —  Complete Protocol Stack         ║")
    print("║       Submission 1  ·  Submission 2  ·  Submission 3        ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    # ── Submission 1: Physical + Data Link ──────────────────────────────
    test_s1_p2p()
    test_s1_hub_star()
    test_s1_switch()
    test_s1_two_stars()

    # ── Submission 2: Network Layer ──────────────────────────────────────
    test_s2_arp_static_routing()
    test_s2_rip()

    # ── Submission 3: Transport + Application ────────────────────────────
    test_s3_chat()
    test_s3_file_transfer()
    test_s3_gobackn_detailed()
    test_s3_full_stack_encapsulation()

    print("\n\n╔══════════════════════════════════════════════════════════════╗")
    print("║                 All test cases completed.                    ║")
    print("╚══════════════════════════════════════════════════════════════╝")
