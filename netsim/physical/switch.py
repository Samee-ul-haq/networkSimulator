"""
Data Link Layer — Switch (Layer 2 device).

Behaviour
---------
- MAC address learning: records {src_mac → port} on every received frame.
- Selective forwarding:
    • Known unicast  → forward to that port only.
    • Unknown unicast or broadcast → flood all ports except sender.
- Each port is a separate collision domain.
- All ports share one broadcast domain (no VLANs).
- Can accept direct Interface connections and Hub uplinks.
"""


class Switch:
    def __init__(self, name: str, num_ports: int):
        self.name       = name
        self.num_ports  = num_ports
        self.ports      = {}        # port_num → Interface | Hub | None
        self.mac_table  = {}        # MAC (str) → port_num (int)
        self._next_port = 0

        for p in range(num_ports):
            self.ports[p] = None

    # ── Connection management ─────────────────────────────────────────── #

    def connect(self, interface):
        """Connect an Interface (from a Node/Router) to the next free port."""
        port = self._alloc_port()
        self.ports[port] = interface
        interface.switch      = self
        interface.switch_port = port
        print(f"[SWITCH {self.name}] port {port} ← {interface.name} ({interface.ip})")
        return port

    def _connect_hub(self, hub):
        """Called by Hub.set_uplink() — reserves a port for the hub."""
        port = self._alloc_port()
        self.ports[port] = hub
        print(f"[SWITCH {self.name}] port {port} ← Hub {hub.name} (uplink)")
        return port

    def _alloc_port(self):
        if self._next_port >= self.num_ports:
            raise RuntimeError(f"Switch {self.name}: all ports occupied")
        p = self._next_port
        self._next_port += 1
        return p

    # ── Frame processing (from Interface) ─────────────────────────────── #

    def transmit(self, frame, sender_iface):
        """Called by a device Interface; sender is the Interface object."""
        sender_port = self._port_of(sender_iface)
        self._learn(frame.src_mac, sender_port)
        self._forward(frame, sender_port)

    # ── Frame processing (from Hub uplink) ────────────────────────────── #

    def _receive_from_hub(self, frame, sender_hub):
        """Called by Hub when a frame arrives on the uplink."""
        sender_port = self._port_of(sender_hub)
        self._learn(frame.src_mac, sender_port)
        self._forward(frame, sender_port)

    # ── Internal MAC logic ─────────────────────────────────────────────── #

    def _learn(self, mac: str, port: int):
        if mac not in self.mac_table:
            self.mac_table[mac] = port
            print(f"[SWITCH {self.name}] MAC learned: {mac} → port {port}")

    def _forward(self, frame, sender_port: int):
        dst = frame.dst_mac.upper()

        if dst == "FF:FF:FF:FF:FF:FF":
            print(f"[SWITCH {self.name}] Broadcast — flooding all ports")
            self._flood(frame, sender_port)
            return

        if dst in self.mac_table:
            target_port = self.mac_table[dst]
            print(f"[SWITCH {self.name}] Unicast {dst} → port {target_port}")
            self._send_to_port(frame, target_port)
        else:
            print(f"[SWITCH {self.name}] Unknown dst {dst} — flooding")
            self._flood(frame, sender_port)

    def _flood(self, frame, exclude_port: int):
        bits = frame.to_bits()
        for port, endpoint in self.ports.items():
            if port == exclude_port or endpoint is None:
                continue
            self._send_to_port(frame, port)

    def _send_to_port(self, frame, port: int):
        endpoint = self.ports[port]
        bits     = frame.to_bits()
        if endpoint is None:
            return
        if hasattr(endpoint, "_broadcast_from_switch"):
            # It's a Hub
            print(f"[SWITCH {self.name}]   port {port} → Hub {endpoint.name}: "
                  f"{len(bits)} bits")
            endpoint._broadcast_from_switch(frame)
        else:
            # It's an Interface
            print(f"[SWITCH {self.name}]   port {port} ({endpoint.name}): "
                  f"{len(bits)} bits")
            endpoint.receive(frame)

    # ── Helpers ───────────────────────────────────────────────────────── #

    def _port_of(self, endpoint):
        for p, e in self.ports.items():
            if e is endpoint:
                return p
        return -1

    def show_mac_table(self):
        print(f"\n  [MAC Table — Switch {self.name}]")
        if not self.mac_table:
            print("    (empty)")
        for mac, port in sorted(self.mac_table.items()):
            print(f"    {mac}  →  port {port}")

    # ── Domain reporting ─────────────────────────────────────────────── #

    @property
    def collision_domains(self):
        """One collision domain per port."""
        return self._next_port

    @property
    def broadcast_domains(self):
        return 1
