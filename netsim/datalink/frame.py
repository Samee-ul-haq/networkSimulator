"""
Data Link Layer — Ethernet Frame (IEEE 802.3)

Structure
---------
  Destination MAC  : 6 bytes
  Source MAC       : 6 bytes
  EtherType        : 2 bytes   (0x0800=IPv4, 0x0806=ARP)
  Payload          : N bytes
  FCS (CRC-32)     : 4 bytes

The Frame Check Sequence is computed over dest+src+ethertype+payload.
"""

import struct
from utils.crc import compute_crc32, verify_crc32


class EthernetFrame:
    BROADCAST = "FF:FF:FF:FF:FF:FF"

    def __init__(self, src_mac: str, dst_mac: str, payload, ethertype: int = 0x0800):
        self.src_mac   = src_mac.upper()
        self.dst_mac   = dst_mac.upper()
        self.ethertype = ethertype
        self.payload   = payload
        self.fcs       = self._compute_fcs()   # CRC-32 over header+payload

    # ── Serialisation helpers ─────────────────────────────────────────── #

    @staticmethod
    def _mac_bytes(mac: str) -> bytes:
        return bytes.fromhex(mac.replace(":", ""))

    def _header_bytes(self) -> bytes:
        return (self._mac_bytes(self.dst_mac) +
                self._mac_bytes(self.src_mac) +
                struct.pack("!H", self.ethertype))

    def _payload_bytes(self) -> bytes:
        p = self.payload
        if isinstance(p, (bytes, bytearray)):
            return bytes(p)
        if isinstance(p, str):
            return p.encode("utf-8")
        if hasattr(p, "to_bytes"):
            return p.to_bytes()
        return str(p).encode("utf-8")

    # ── CRC ──────────────────────────────────────────────────────────── #

    def _compute_fcs(self) -> int:
        return compute_crc32(self._header_bytes() + self._payload_bytes())

    def verify_fcs(self) -> bool:
        return verify_crc32(
            self._header_bytes() + self._payload_bytes(),
            self.fcs
        )

    # ── Physical layer representation ─────────────────────────────────── #

    def to_bits(self) -> str:
        """Convert entire frame (header + payload + FCS) to a bit string."""
        raw = (self._header_bytes() +
               self._payload_bytes() +
               struct.pack("!I", self.fcs))
        return "".join(format(b, "08b") for b in raw)

    # ── Display ──────────────────────────────────────────────────────── #

    def show(self):
        fcs_ok = self.verify_fcs()
        print("  ┌─────────────────────────────┐")
        print("  │       ETHERNET FRAME        │")
        print("  ├─────────────────────────────┤")
        print(f"  │ Dst MAC  : {self.dst_mac}")
        print(f"  │ Src MAC  : {self.src_mac}")
        print(f"  │ EtherType: 0x{self.ethertype:04X}"
              f"  ({'IPv4' if self.ethertype==0x0800 else 'ARP' if self.ethertype==0x0806 else '?'})")
        print(f"  │ Payload  : {type(self.payload).__name__}")
        print(f"  │ FCS(CRC) : {self.fcs:#010x}  [{'✓ valid' if fcs_ok else '✗ ERROR'}]")
        print("  └─────────────────────────────┘")
