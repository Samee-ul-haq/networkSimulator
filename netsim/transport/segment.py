"""
Transport Layer — TCP Segment (simplified RFC 793).

Header fields: src_port, dst_port, seq_num, ack_num, flags, checksum.
Checksum is an Internet-style 16-bit one's-complement sum over the data.
"""

import struct


class TCPSegment:
    # Flag bits
    FLAG_FIN = 0x01
    FLAG_SYN = 0x02
    FLAG_RST = 0x04
    FLAG_ACK = 0x10

    def __init__(self, src_port: int, dst_port: int,
                 seq_num: int, ack_num: int,
                 data, flags: int = 0):
        self.src_port = src_port
        self.dst_port = dst_port
        self.seq_num  = seq_num
        self.ack_num  = ack_num
        self.data     = data
        self.flags    = flags
        self.checksum = self._compute_checksum()

    # ── Checksum ──────────────────────────────────────────────────────── #

    def _data_bytes(self) -> bytes:
        d = self.data
        if isinstance(d, (bytes, bytearray)):
            return bytes(d)
        return str(d).encode("utf-8")

    def _compute_checksum(self) -> int:
        data_b = self._data_bytes()
        total  = (self.src_port + self.dst_port +
                  self.seq_num  + self.ack_num  +
                  self.flags    + sum(data_b))
        return total % 65535

    def verify_checksum(self) -> bool:
        return self._compute_checksum() == self.checksum

    # ── Serialisation ─────────────────────────────────────────────────── #

    def to_bytes(self) -> bytes:
        data_b = self._data_bytes()
        header = struct.pack(
            "!HHIIHHHH",
            self.src_port,
            self.dst_port,
            self.seq_num,
            self.ack_num,
            (5 << 12) | self.flags,  # data offset (5 words) + flags
            65535,                    # window size
            self.checksum,
            0,                        # urgent pointer
        )
        return header + data_b

    # ── Display ───────────────────────────────────────────────────────── #

    def show(self):
        cs_ok = self.verify_checksum()
        flags_str = "|".join(
            name for bit, name in [
                (self.FLAG_SYN, "SYN"), (self.FLAG_ACK, "ACK"),
                (self.FLAG_FIN, "FIN"), (self.FLAG_RST, "RST"),
            ] if self.flags & bit
        ) or "—"

        print("  ┌──────────────────────────┐")
        print("  │       TCP SEGMENT        │")
        print("  ├──────────────────────────┤")
        print(f"  │ Src Port  : {self.src_port}")
        print(f"  │ Dst Port  : {self.dst_port}")
        print(f"  │ Seq Num   : {self.seq_num}")
        print(f"  │ Ack Num   : {self.ack_num}")
        print(f"  │ Flags     : {flags_str}")
        print(f"  │ Checksum  : {self.checksum:#06x}  "
              f"[{'✓' if cs_ok else '✗ ERROR'}]")
        print(f"  │ Data      : {self.data!r}")
        print("  └──────────────────────────┘")
