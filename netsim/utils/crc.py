"""
CRC-32 implementation using polynomial 0x04C11DB7 (Ethernet standard).
Used by the Data Link layer for Frame Check Sequence (FCS).
"""


def compute_crc32(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            if crc & 0x80000000:
                crc = (crc << 1) ^ 0x04C11DB7
            else:
                crc <<= 1
            crc &= 0xFFFFFFFF
    return crc ^ 0xFFFFFFFF


def verify_crc32(data: bytes, expected: int) -> bool:
    return compute_crc32(data) == expected
