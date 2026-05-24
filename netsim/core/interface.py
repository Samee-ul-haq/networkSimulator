from utils.ip_utils import strip_prefix, get_prefix_len


class Interface:
    """
    Represents a network interface card (NIC) on a Node or Router.
    Knows its own IP/MAC, and which physical medium it is connected to.
    """

    def __init__(self, name: str, ip: str, mac: str):
        self.name = name          # e.g. "eth0"
        self.ip   = ip            # e.g. "192.168.1.2/24"
        self.mac  = mac           # e.g. "AA:BB:CC:DD:EE:FF"
        self.node = None          # set by Node.add_interface()

        # Exactly one of these will be set when the interface is connected:
        self.channel = None       # point-to-point Channel
        self.hub     = None       # Hub
        self.switch  = None       # Switch

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def ip_addr(self) -> str:
        return strip_prefix(self.ip)

    def prefix_len(self) -> int:
        return get_prefix_len(self.ip)

    # ------------------------------------------------------------------ #
    #  Downward (transmit)                                                 #
    # ------------------------------------------------------------------ #

    def transmit(self, frame):
        """Push a frame out onto the connected medium."""
        bits = frame.to_bits()
        print(f"[PHYSICAL] {self.name} → {len(bits)}-bit signal on wire")

        if self.channel:
            self.channel.transmit(frame, self)
        elif self.hub:
            self.hub.transmit(frame, self)
        elif self.switch:
            self.switch.transmit(frame, self)
        else:
            print(f"[PHYSICAL] {self.name}: not connected to any medium — frame dropped")

    # ------------------------------------------------------------------ #
    #  Upward (receive)                                                    #
    # ------------------------------------------------------------------ #

    def receive(self, frame):
        """Called by the medium when a frame arrives at this interface."""
        if self.node:
            self.node.receive_frame(frame, incoming_interface=self)

    def __repr__(self):
        return f"Interface({self.name}, {self.ip}, {self.mac})"
