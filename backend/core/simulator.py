class Simulator:

    devices = []

    @classmethod
    def add_device(cls, device):

        cls.devices.append(device)

    @classmethod
    def find_device_by_ip(cls, ip):

        for device in cls.devices:

            for interface in device.interfaces:

                interface_ip = interface.ip.split("/")[0]

                if interface_ip == ip:
                    return device

        return None