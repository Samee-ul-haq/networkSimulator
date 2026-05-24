import ipaddress


def get_network(ip_with_mask):
    """
    Returns network address.
    Example:
    192.168.1.10/24 -> 192.168.1.0/24
    """

    network = ipaddress.ip_network(
        ip_with_mask,
        strict=False
    )

    return str(network)


def same_subnet(ip1, ip2):
    """
    Checks whether two IPs belong
    to same subnet.
    """

    net1 = ipaddress.ip_network(
        ip1,
        strict=False
    )

    net2 = ipaddress.ip_network(
        ip2,
        strict=False
    )

    return net1.network_address == net2.network_address


def longest_prefix_match(destination_ip,
                         routes):
    """
    Finds best route using
    longest prefix matching.
    """

    best_route = None
    longest_prefix = -1

    dest = ipaddress.ip_address(destination_ip)

    for route in routes:

        network = ipaddress.ip_network(
            f"{route.network}/{route.mask}",
            strict=False
        )

        if dest in network:

            prefix = network.prefixlen

            if prefix > longest_prefix:
                longest_prefix = prefix
                best_route = route

    return best_route