class EthernetFrame:
    def __init__(self,
                 src_mac,
                 dst_mac,
                 payload):
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.payload = payload