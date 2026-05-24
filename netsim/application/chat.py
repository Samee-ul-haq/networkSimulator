"""
Application Layer — Chat Service (port 5000).

Provides send/receive for instant text messages.
Integrates with the Node's full protocol stack for end-to-end delivery.
"""

from transport.port_manager import PortManager


class ChatApp:
    PORT = PortManager.WELL_KNOWN_PORTS["CHAT"]   # 5000

    def __init__(self, node):
        self.node     = node
        self.inbox    = []   # list of (from_ip, message)
        node.register_process(self.PORT, "Chat Service")

    # ── Send ──────────────────────────────────────────────────────────── #

    def send(self, message: str, destination_ip: str, gateway: str):
        """
        Passes message down the full protocol stack:
        ChatApp → TCP Segment → IP Packet → Ethernet Frame → wire.
        """
        print(f"\n[CHAT APP] {self.node.name} → '{message}' to {destination_ip}")

        self.node.send_data(
            destination_ip   = destination_ip,
            message          = message,
            gateway          = gateway,
            source_port      = PortManager.allocate_ephemeral_port(),
            destination_port = self.PORT,
            sequence_number  = 0,
        )

    # ── Receive ───────────────────────────────────────────────────────── #

    def on_receive(self, data: str, from_ip: str):
        """Called by Node when a segment arrives on this port."""
        self.inbox.append((from_ip, data))
        print(f"[CHAT APP] {self.node.name} ← '{data}' from {from_ip}")

    # ── Utility ───────────────────────────────────────────────────────── #

    def show_inbox(self):
        print(f"\n[CHAT APP] Inbox for {self.node.name}:")
        if not self.inbox:
            print("  (empty)")
        for src, msg in self.inbox:
            print(f"  [{src}]: {msg}")
