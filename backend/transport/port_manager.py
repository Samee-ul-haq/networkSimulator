class PortManager:

    WELL_KNOWN_PORTS = {
        "CHAT": 5000,
        "FILE_TRANSFER": 5010
    }

    ephemeral_port = 49152

    @classmethod
    def allocate_ephemeral_port(cls):
        port = cls.ephemeral_port
        cls.ephemeral_port += 1
        return port