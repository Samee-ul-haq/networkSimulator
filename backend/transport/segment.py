class TCPSegment:

    def __init__(self,
                 src_port,
                 dst_port,
                 seq_num,
                 ack_num,
                 data):

        self.src_port = src_port
        self.dst_port = dst_port
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.data = data

    def show(self):
        print("\n[TCP SEGMENT]")
        print(f"Source Port      : {self.src_port}")
        print(f"Destination Port : {self.dst_port}")
        print(f"Sequence Number  : {self.seq_num}")
        print(f"ACK Number       : {self.ack_num}")
        print(f"Data             : {self.data}")