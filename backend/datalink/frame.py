class EthernetFrame:
    def __init__(self,
                 src_mac,
                 dst_mac,
                 payload):

        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.payload = payload

    def show(self):

        print("\n[ETHERNET FRAME]")

        print(f"Source MAC      : {self.src_mac}")
        print(f"Destination MAC : {self.dst_mac}")

        print(
            f"Payload          : "
            f"{type(self.payload).__name__}"
        )