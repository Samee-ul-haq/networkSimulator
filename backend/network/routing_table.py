class Route:
    def __init__(self,
                 network,
                 mask,
                 next_hop,
                 interface):
        self.network = network
        self.mask = mask
        self.next_hop = next_hop
        self.interface = interface