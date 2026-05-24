"""
Physical Layer — Point-to-Point Channel (full-duplex link).

Connects exactly two Interface endpoints.
Simulates bit-level transmission: logs bit count, delivers frame object.
"""


class Channel:
    def __init__(self, name: str = "link"):
        self.name        = name
        self.endpoint_a  = None   # Interface
        self.endpoint_b  = None   # Interface

    def connect(self, iface_a, iface_b):
        """Attach two interfaces to the two ends of this channel."""
        self.endpoint_a = iface_a
        self.endpoint_b = iface_b
        iface_a.channel = self
        iface_b.channel = self
        print(f"[PHYSICAL] Link '{self.name}': "
              f"{iface_a.name} ({iface_a.ip}) ←→ {iface_b.name} ({iface_b.ip})")

    def transmit(self, frame, sender_iface):
        """Forward frame from sender to the other endpoint."""
        bits = frame.to_bits()
        print(f"[PHYSICAL] '{self.name}': {len(bits)} bits propagating …")

        if sender_iface is self.endpoint_a:
            receiver = self.endpoint_b
        else:
            receiver = self.endpoint_a

        print(f"[PHYSICAL] Signal arrives at {receiver.name}")
        receiver.receive(frame)
