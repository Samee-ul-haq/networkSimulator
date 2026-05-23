class TCPSegment:
    def __init__(self,
                 src_port,
                 dst_port,
                 seq,
                 ack,
                 data):
        self.src_port = src_port
        self.dst_port = dst_port
        self.seq = seq
        self.ack = ack
        self.data = data