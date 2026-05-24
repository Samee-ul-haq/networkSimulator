import ipaddress


def get_network_address(ip_with_prefix: str) -> str:
    net = ipaddress.ip_network(ip_with_prefix, strict=False)
    return str(net.network_address)


def same_subnet(ip1_prefix: str, ip2_prefix: str) -> bool:
    n1 = ipaddress.ip_network(ip1_prefix, strict=False)
    n2 = ipaddress.ip_network(ip2_prefix, strict=False)
    return n1.network_address == n2.network_address


def longest_prefix_match(destination_ip: str, routes: list):
    """
    Returns the best Route object from a list using longest prefix match.
    Routes must have .network and .mask attributes.
    """
    best_route = None
    longest_prefix = -1
    dest = ipaddress.ip_address(destination_ip)

    for route in routes:
        network = ipaddress.ip_network(
            f"{route.network}/{route.mask}", strict=False
        )
        if dest in network:
            plen = network.prefixlen
            if plen > longest_prefix:
                longest_prefix = plen
                best_route = route

    return best_route


def strip_prefix(ip_with_prefix: str) -> str:
    return ip_with_prefix.split("/")[0]


def get_prefix_len(ip_with_prefix: str) -> int:
    parts = ip_with_prefix.split("/")
    return int(parts[1]) if len(parts) == 2 else 32
