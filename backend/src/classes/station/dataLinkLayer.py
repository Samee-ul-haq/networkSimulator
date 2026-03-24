from src.utils.encode import encodeData
from src.utils.decode import decodeData


class senderSideDataLink:
    def __init__(self, device):
        self.device = device

    def send(self, dest, data, medium):
        """
        Public method called by device.send().
        Builds frame and passes to physical layer.
        """
        src = self.device.macAddress
        length = len(data)
        self.conversion(dest, src, length, data, medium)

    def conversion(self, dest, src, length, data, medium):
        """
        Builds Ethernet frame:
          dest_mac  (6 bytes)
          src_mac   (6 bytes)
          length    (2 bytes)
          data      (N bytes)
          crc       (4 bytes)
        Converts to bit string and passes down to physical layer.
        """

        # ── Inner helpers ─────────────────────────────────────────────
        def mac_to_bytes(mac):
            return bytes.fromhex(mac.replace(":", ""))

        def length_to_bytes(n):
            return n.to_bytes(2, 'big')

        def data_to_bytes(d):
            return d.encode('utf-8')

        def crc_to_bytes(crc_str):
            # CRC from encodeData is a bit string e.g. '1011'
            # Pad to 32 bits and convert to int then bytes
            padded = crc_str.zfill(32)
            return int(padded, 2).to_bytes(4, 'big')

        def bytes_to_bits(byte_data):
            return ''.join(format(byte, '08b') for byte in byte_data)

        # ── Build CRC ─────────────────────────────────────────────────
        # encodeData expects a bit string — convert data to bits first
        data_bits = bytes_to_bits(data_to_bytes(data))
        crc = encodeData(data_bits)   # returns bit string remainder

        # ── Assemble frame bytes ──────────────────────────────────────
        frame = {
            'dest_mac': mac_to_bytes(dest),
            'src_mac' : mac_to_bytes(src),
            'length'  : length_to_bytes(length),
            'data'    : data_to_bytes(data),
            'crc'     : crc_to_bytes(crc)
        }

        byte_string = (frame['dest_mac'] + frame['src_mac'] +
                       frame['length']   + frame['data']    +
                       frame['crc'])
        bits_string = bytes_to_bits(byte_string)

        print(f"[DL SENDER] Frame built: dest={dest}, src={src}, "
              f"len={length}, crc={crc}")
        self.callSenderPhysical(bits_string, medium)

    def callSenderPhysical(self, bit_string, medium):
        self.device.senderSidePhysical.transmitToMedium(bit_string, medium)


# ─────────────────────────────────────────────────────────────────────────── #

class recieverSideDataLink:
    def __init__(self, device):
        self.device = device

    def receive(self, bits_string):
        """
        Called by physical layer after full frame received.
        Steps:
          1. Convert bits -> bytes
          2. Parse frame fields
          3. Verify CRC
          4. Check destination MAC matches this device
          5. Deliver data to upper layer if all checks pass
        Returns True on success, False on any failure.
        """

        # ── Step 1: bits -> bytes ─────────────────────────────────────
        def bits_to_bytes(bit_string):
            # Pad to multiple of 8 just in case
            pad = (8 - len(bit_string) % 8) % 8
            bit_string = bit_string + '0' * pad
            return bytes(
                int(bit_string[i:i+8], 2)
                for i in range(0, len(bit_string), 8)
            )

        def bytes_to_bits(byte_data):
            return ''.join(format(byte, '08b') for byte in byte_data)

        try:
            byte_string = bits_to_bytes(bits_string)
        except Exception as e:
            print(f"[DL RECV] {self.device.name} bit->byte conversion failed: {e}")
            return False

        # ── Step 2: Parse frame fields ────────────────────────────────
        dest   = byte_string[0:6]
        src    = byte_string[6:12]
        length = byte_string[12:14]
        length = int.from_bytes(length, 'big')
        data   = byte_string[14:14 + length]
        crc    = byte_string[14 + length:]

        crc_int = int.from_bytes(crc, 'big')
        dest_mac = ':'.join(f'{b:02X}' for b in dest)
        src_mac  = ':'.join(f'{b:02X}' for b in src)

        try:
            data_str = data.decode('utf-8')
        except Exception:
            print(f"[DL RECV] {self.device.name} data decode failed.")
            return False

        # ── Step 3: Verify CRC ────────────────────────────────────────
        data_bits = bytes_to_bits(data)
        crc_bits  = format(crc_int, '032b')          # 32-bit CRC as bit string
        codeword  = data_bits + crc_bits

        crc_valid, _ = decodeData(codeword)

        if not crc_valid:
            print(f"[DL RECV] {self.device.name} CRC ERROR — frame dropped.")
            return False

        # ── Step 4: MAC address check ─────────────────────────────────
        my_mac = self.device.macAddress
        broadcast = "FF:FF:FF:FF:FF:FF"

        if dest_mac != my_mac and dest_mac != broadcast:
            print(f"[DL RECV] {self.device.name} MAC mismatch "
                  f"(frame for {dest_mac}) — dropped.")
            return False

        # ── Step 5: Deliver to upper layer ────────────────────────────
        frame = {
            "dest_mac" : dest_mac,
            "src_mac"  : src_mac,
            "length"   : length,
            "data"     : data_str,
            "crc"      : crc_int
        }

        print(f"[DL RECV] {self.device.name} received frame from {src_mac}: "
              f"'{data_str}'")
        self.deliverToUpperLayer(frame)
        return True

    def deliverToUpperLayer(self, frame):
        """Pass frame up to Network layer (or just store/print for now)."""
        print(f"[NETWORK] {self.device.name} got message: '{frame['data']}' "
              f"from {frame['src_mac']}")
