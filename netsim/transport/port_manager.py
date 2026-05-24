"""
Transport Layer — Port Manager.

Well-known ports : 0–1023     (IANA assigned)
Registered ports : 1024–49151
Ephemeral ports  : 49152–65535 (OS-assigned for outgoing connections)
"""


class PortManager:
    WELL_KNOWN_PORTS = {
        "FTP_DATA"     : 20,
        "FTP"          : 21,
        "SSH"          : 22,
        "TELNET"       : 23,
        "SMTP"         : 25,
        "DNS"          : 53,
        "HTTP"         : 80,
        "POP3"         : 110,
        "IMAP"         : 143,
        "HTTPS"        : 443,
        # Application-layer services defined in this simulator
        "CHAT"         : 5000,
        "FILE_TRANSFER": 5010,
    }

    _ephemeral_next = 49152

    @classmethod
    def allocate_ephemeral_port(cls) -> int:
        port = cls._ephemeral_next
        cls._ephemeral_next += 1
        if cls._ephemeral_next > 65535:
            cls._ephemeral_next = 49152
        return port

    @classmethod
    def reset(cls):
        cls._ephemeral_next = 49152

    @classmethod
    def is_well_known(cls, port: int) -> bool:
        return port < 1024

    @classmethod
    def is_ephemeral(cls, port: int) -> bool:
        return 49152 <= port <= 65535

    @classmethod
    def port_name(cls, port: int) -> str:
        for name, p in cls.WELL_KNOWN_PORTS.items():
            if p == port:
                return name
        return str(port)
