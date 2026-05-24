"""
Physical Layer — Hub (multiport repeater, Layer 1 device).

Behaviour
---------
- Broadcasts every received frame to ALL other ports (no filtering).
- Implements CSMA/CD:
    • Carrier Sense  — checks if medium is currently busy.
    • Collision Detect — detects simultaneous transmissions.
    • Exponential Backoff — waits before retrying after a collision.
- One collision domain, one broadcast domain.
- Can be connected to a Switch via set_uplink().
"""

import random
import time


class Hub:
    def __init__(self, name: str, num_ports: int):
        self.name         = name
        self.num_ports    = num_ports
        self.ports        = {}          # port_num (int) → Interface | None
        self._next_port   = 0
        self._busy        = False       # CSMA/CD carrier-sense flag
        self._uplink      = None        # connected Switch (optional)

        for p in range(num_ports):
            self.ports[p] = None

    # ── Connection management ─────────────────────────────────────────── #

    def connect(self, interface):
        """Connect an Interface to the next free port."""
        if self._next_port >= self.num_ports:
            raise RuntimeError(f"Hub {self.name}: all ports occupied")
        port = self._next_port
        self.ports[port] = interface
        interface.hub      = self
        interface.hub_port = port
        self._next_port   += 1
        print(f"[HUB {self.name}] port {port} ← {interface.name} ({interface.ip})")
        return port

    def set_uplink(self, switch):
        """Connect this hub's uplink to a Switch."""
        self._uplink = switch
        switch._connect_hub(self)
        print(f"[HUB {self.name}] uplink → Switch {switch.name}")

    # ── CSMA/CD transmission ──────────────────────────────────────────── #

    def transmit(self, frame, sender_iface, _retry: int = 0):
        """
        Called by a device's Interface when it wants to send.
        Implements full CSMA/CD with exponential backoff.
        """
        # ── Carrier Sense ──────────────────────────────────────────────
        if self._busy:
            print(f"[CSMA/CD] Hub {self.name}: medium BUSY — "
                  f"{sender_iface.name} defers")
            self._backoff(frame, sender_iface, _retry)
            return

        # ── Collision Detect (simulate: two simultaneous sends) ────────
        # In a real system collisions occur at the electrical level.
        # We simulate by flagging _busy = True and checking again.
        self._busy = True

        sender_port = self._port_of(sender_iface)
        print(f"\n[HUB {self.name}] Broadcast from port {sender_port} "
              f"({sender_iface.name}) → all other ports")

        # ── Broadcast ─────────────────────────────────────────────────
        bits = frame.to_bits()
        for port, iface in self.ports.items():
            if port != sender_port and iface is not None:
                print(f"[HUB {self.name}]   port {port} ({iface.name}): "
                      f"{len(bits)} bits received")
                iface.receive(frame)

        # ── Forward to uplink switch if present ───────────────────────
        if self._uplink:
            print(f"[HUB {self.name}]   uplink → Switch {self._uplink.name}")
            self._uplink._receive_from_hub(frame, self)

        self._busy = False

    def _backoff(self, frame, iface, attempt):
        """Exponential backoff: wait 0..2^k - 1 slot times, then retry."""
        k         = min(attempt + 1, 10)
        slots     = random.randint(0, (2 ** k) - 1)
        wait_ms   = slots * 0.512           # 512 µs slot time (Ethernet)
        print(f"[CSMA/CD] Backoff attempt {k}: waiting {slots} slot(s) "
              f"({wait_ms:.3f} ms simulated)")
        time.sleep(wait_ms / 1000)
        self.transmit(frame, iface, _retry=attempt + 1)

    # ── Called by Switch to inject a frame into this hub's domain ────── #

    def _broadcast_from_switch(self, frame):
        """Switch calls this to flood a frame into this hub's segment."""
        print(f"[HUB {self.name}] Frame injected from switch — broadcasting")
        bits = frame.to_bits()
        for iface in self.ports.values():
            if iface is not None:
                print(f"[HUB {self.name}]   → {iface.name}: {len(bits)} bits")
                iface.receive(frame)

    # ── Helpers ───────────────────────────────────────────────────────── #

    def _port_of(self, iface):
        for p, i in self.ports.items():
            if i is iface:
                return p
        return -1

    # ── Domain reporting ─────────────────────────────────────────────── #

    @property
    def collision_domains(self):
        return 1   # entire hub = one collision domain

    @property
    def broadcast_domains(self):
        return 1
