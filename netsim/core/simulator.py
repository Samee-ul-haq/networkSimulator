"""
Simulator — global device registry.
Allows any layer to look up a device by IP or MAC without circular imports.
"""


class Simulator:
    _devices: list = []

    @classmethod
    def add_device(cls, device):
        cls._devices.append(device)

    @classmethod
    def reset(cls):
        cls._devices.clear()

    @classmethod
    def find_by_ip(cls, ip: str):
        for dev in cls._devices:
            for iface in dev.interfaces:
                if iface.ip_addr() == ip:
                    return dev
        return None

    @classmethod
    def find_by_mac(cls, mac: str):
        for dev in cls._devices:
            for iface in dev.interfaces:
                if iface.mac.upper() == mac.upper():
                    return dev
        return None

    @classmethod
    def find_interface_by_ip(cls, ip: str):
        for dev in cls._devices:
            for iface in dev.interfaces:
                if iface.ip_addr() == ip:
                    return iface
        return None

    @classmethod
    def show_all(cls):
        print("\n[SIMULATOR] Registered devices:")
        for dev in cls._devices:
            dev.show_interfaces()
