class PortManager:
    WELL_KNOWN = {
        "CHAT": 5000,
        "FTP": 21
    }

    ephemeral = 49152

    @classmethod
    def allocate(cls):
        port = cls.ephemeral
        cls.ephemeral += 1
        return port