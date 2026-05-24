"""
Network Layer — IPv4 Packet (simplified RFC 791).

Header fields simulated:
  Version, IHL, TTL, Protocol, Src IP, Dst IP, Total Length.
Checksum is omitted for brevity (routers verify FCS at L2 instead).
"""

import struct
import socket


class IPPacket:
    PROTO_TCP = 6
    PROTO_UDP = 17

    def __init__(self, src_ip: str, dst_ip: str, payload,
                 protocol: int = PROTO_TCP, ttl: int = 64):
        self.version  = 4
        self.src_ip   = src_ip
        self.dst_ip   = dst_ip
        self.payload  = payload
        self.protocol = protocol
        self.ttl      = ttl

    # ── Serialisation ─────────────────────────────────────────────────── #

    def _payload_bytes(self) -> bytes:
        p = self.payload
        if isinstance(p, (bytes, bytearray)):
            return bytes(p)
        if isinstance(p, str):
            return p.encode("utf-8")
        if hasattr(p, "to_bytes"):
            return p.to_bytes()
        return str(p).encode("utf-8")

    def to_bytes(self) -> bytes:
        payload_b    = self._payload_bytes()
        total_length = 20 + len(payload_b)
        header = struct.pack(
            "!BBHHHBBH4s4s",
            (self.version << 4) | 5,   # version + IHL (5×32-bit words)
            0,                          # DSCP/ECN
            total_length,
            0,                          # Identification
            0,                          # Flags + Fragment Offset
            self.ttl,
            self.protocol,
            0,                          # Header checksum (simplified)
            socket.inet_aton(self.src_ip),
            socket.inet_aton(self.dst_ip),
        )
        return header + payload_b

    # ── TTL management ─────────────────────────────────────────────────── #

    def decrement_ttl(self) -> bool:
        """Decrements TTL; returns False if packet should be dropped."""
        self.ttl -= 1
        return self.ttl > 0

    # ── Display ───────────────────────────────────────────────────────── #

    def show(self):
        proto = {6: "TCP", 17: "UDP"}.get(self.protocol, str(self.protocol))
        print("  ┌───────────────────────┐")
        print("  │      IP PACKET        │")
        print("  ├───────────────────────┤")
        print(f"  │ Version  : IPv{self.version}")
        print(f"  │ TTL      : {self.ttl}")
        print(f"  │ Protocol : {proto}")
        print(f"  │ Src IP   : {self.src_ip}")
        print(f"  │ Dst IP   : {self.dst_ip}")
        print(f"  │ Payload  : {type(self.payload).__name__}")
        print("  └───────────────────────┘")
