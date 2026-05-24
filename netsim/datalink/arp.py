"""
Data Link Layer — ARP (Address Resolution Protocol)
Implements dynamic ARP: broadcasts ARP Request, processes ARP Reply.
RFC 826.
"""


# ──────────────────────────────────────────────────────────────────────── #
#  ARP Message types                                                        #
# ──────────────────────────────────────────────────────────────────────── #

class ARPRequest:
    ETHERTYPE = 0x0806

    def __init__(self, sender_ip, sender_mac, target_ip):
        self.sender_ip  = sender_ip
        self.sender_mac = sender_mac
        self.target_ip  = target_ip

    def to_bytes(self) -> bytes:
        return (f"ARP_REQ:{self.sender_ip}:{self.sender_mac}"
                f":{self.target_ip}").encode()

    def __repr__(self):
        return (f"ARPRequest(who has {self.target_ip}? "
                f"tell {self.sender_ip}/{self.sender_mac})")


class ARPReply:
    ETHERTYPE = 0x0806

    def __init__(self, sender_ip, sender_mac, target_ip, target_mac):
        self.sender_ip  = sender_ip
        self.sender_mac = sender_mac
        self.target_ip  = target_ip
        self.target_mac = target_mac

    def to_bytes(self) -> bytes:
        return (f"ARP_REP:{self.sender_ip}:{self.sender_mac}"
                f":{self.target_ip}:{self.target_mac}").encode()

    def __repr__(self):
        return f"ARPReply({self.sender_ip} is at {self.sender_mac})"


# ──────────────────────────────────────────────────────────────────────── #
#  ARP Table                                                                #
# ──────────────────────────────────────────────────────────────────────── #

class ARPTable:
    """
    Per-node ARP cache.
    Supports static pre-population AND dynamic resolution via broadcast.
    """

    def __init__(self, owner=None):
        self._table = {}       # IP (str) → MAC (str)
        self.owner  = owner    # Node that owns this table

    # ── Cache management ─────────────────────────────────────────────── #

    def add_entry(self, ip: str, mac: str):
        self._table[ip] = mac
        print(f"[ARP]  Cache updated: {ip} → {mac}")

    def resolve(self, ip: str):
        return self._table.get(ip)

    # ── Dynamic resolution ───────────────────────────────────────────── #

    def resolve_or_request(self, target_ip: str, sender_interface):
        """
        Return MAC if cached; otherwise broadcast ARP Request and wait
        for the reply (synchronous in this simulator — reply arrives
        within the same call stack via hub/channel).
        """
        cached = self.resolve(target_ip)
        if cached:
            print(f"[ARP]  Cache hit : {target_ip} → {cached}")
            return cached

        print(f"[ARP]  Cache miss for {target_ip} — broadcasting ARP Request")
        self._send_request(target_ip, sender_interface)

        # By the time _send_request returns, the reply has already been
        # processed synchronously and the cache is populated.
        resolved = self.resolve(target_ip)
        if resolved:
            print(f"[ARP]  Resolved  : {target_ip} → {resolved}")
        else:
            print(f"[ARP]  FAILED    : no reply for {target_ip}")
        return resolved

    # ── Internal helpers ─────────────────────────────────────────────── #

    def _send_request(self, target_ip: str, sender_interface):
        from datalink.frame import EthernetFrame

        sender_ip  = sender_interface.ip_addr()
        sender_mac = sender_interface.mac

        req   = ARPRequest(sender_ip, sender_mac, target_ip)
        frame = EthernetFrame(
            src_mac   = sender_mac,
            dst_mac   = "FF:FF:FF:FF:FF:FF",
            payload   = req,
            ethertype = 0x0806,
        )
        print(f"[ARP]  → ARP Request broadcast: who has {target_ip}?")
        sender_interface.transmit(frame)

    def handle_arp_request(self, req: ARPRequest, recv_interface):
        """Called when the owning node receives an ARP Request frame."""
        # Always cache the sender
        self.add_entry(req.sender_ip, req.sender_mac)

        my_ip = recv_interface.ip_addr()
        if my_ip == req.target_ip:
            print(f"[ARP]  ARP Request is for me ({my_ip}) — sending Reply")
            self._send_reply(req, recv_interface)
        # else: not for us, silently ignore

    def _send_reply(self, req: ARPRequest, sender_interface):
        from datalink.frame import EthernetFrame

        my_ip  = sender_interface.ip_addr()
        my_mac = sender_interface.mac

        rep   = ARPReply(my_ip, my_mac, req.sender_ip, req.sender_mac)
        frame = EthernetFrame(
            src_mac   = my_mac,
            dst_mac   = req.sender_mac,
            payload   = rep,
            ethertype = 0x0806,
        )
        print(f"[ARP]  → ARP Reply: {my_ip} is at {my_mac}")
        sender_interface.transmit(frame)

    def handle_arp_reply(self, rep: ARPReply):
        """Called when the owning node receives an ARP Reply frame."""
        print(f"[ARP]  ← ARP Reply received: {rep.sender_ip} is at {rep.sender_mac}")
        self.add_entry(rep.sender_ip, rep.sender_mac)

    # ── Display ──────────────────────────────────────────────────────── #

    def show(self):
        owner_name = self.owner.name if self.owner else "?"
        print(f"\n  [ARP Table — {owner_name}]")
        if not self._table:
            print("    (empty)")
        for ip, mac in self._table.items():
            print(f"    {ip:<18} →  {mac}")
