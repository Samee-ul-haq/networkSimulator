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

    def __str__(self):

        return (
            f"{self.network}/{self.mask} "
            f"via {self.next_hop} "
            f"dev {self.interface}"
        )