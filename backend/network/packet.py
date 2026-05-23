class IPPacket:
    def __init__(self,
                 src_ip,
                 dst_ip,
                 payload):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.payload = payload