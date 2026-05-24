"""
Network Layer — Routing Table with Longest Prefix Match (RFC 1812).
"""

import ipaddress


class Route:
    def __init__(self, network: str, mask: str,
                 next_hop: str, interface: str, metric: int = 1):
        self.network   = network     # e.g. "10.0.0.0"
        self.mask      = str(mask)   # e.g. "24"
        self.next_hop  = next_hop    # "direct" or IP string
        self.interface = interface   # e.g. "eth0"
        self.metric    = metric      # hop count / cost

    def __str__(self):
        nh = "directly connected" if self.next_hop == "direct" else f"via {self.next_hop}"
        return (f"{self.network}/{self.mask:<4} "
                f"{nh:<24} dev {self.interface:<6} metric {self.metric}")


class RoutingTable:
    def __init__(self, owner_name: str = ""):
        self.routes     = []
        self.owner_name = owner_name

    def add_route(self, route: Route):
        """Add or update a route (update if same prefix and new metric is better)."""
        for i, existing in enumerate(self.routes):
            if existing.network == route.network and existing.mask == route.mask:
                if route.metric < existing.metric:
                    self.routes[i] = route
                return
        self.routes.append(route)

    def remove_route(self, network: str, mask: str):
        self.routes = [r for r in self.routes
                       if not (r.network == network and r.mask == str(mask))]

    def lookup(self, destination_ip: str):
        """
        Longest Prefix Match.
        Returns the best Route or None if no match found.
        """
        best_route     = None
        longest_prefix = -1
        dest           = ipaddress.ip_address(destination_ip)

        for route in self.routes:
            net = ipaddress.ip_network(
                f"{route.network}/{route.mask}", strict=False
            )
            if dest in net and net.prefixlen > longest_prefix:
                longest_prefix = net.prefixlen
                best_route     = route

        return best_route

    def show(self):
        print(f"\n  ┌── Routing Table [{self.owner_name}] ─────────────────────────────┐")
        if not self.routes:
            print("  │  (empty)")
        for r in self.routes:
            print(f"  │  {r}")
        print("  └────────────────────────────────────────────────────────────┘")
