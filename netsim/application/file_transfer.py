"""
Application Layer — File Transfer Service (port 5010).

Splits a file into fixed-size chunks.
Transfers them using Go-Back-N at the transport layer.
Reassembles received chunks in sequence-number order at the receiver.
"""

from transport.port_manager import PortManager
from transport.gobackn     import GoBackNSender, GoBackNReceiver
from transport.segment     import TCPSegment


class FileTransferApp:
    PORT = PortManager.WELL_KNOWN_PORTS["FILE_TRANSFER"]   # 5010

    def __init__(self, node=None, chunk_size: int = 10):
        self.node          = node
        self.chunk_size    = chunk_size
        self._recv_chunks  = {}    # seq_num → data (for reassembly)

        if node is not None:
            node.register_process(self.PORT, "File Transfer Service")

    # ── Sender side ───────────────────────────────────────────────────── #

    def split(self, data: str) -> list:
        """Divide data into chunks of at most chunk_size characters."""
        chunks = [data[i:i + self.chunk_size]
                  for i in range(0, len(data), self.chunk_size)]
        print(f"\n[FTP] '{data[:20]}{'…' if len(data)>20 else ''}' "
              f"→ {len(chunks)} chunk(s) × {self.chunk_size} bytes")
        for i, c in enumerate(chunks):
            print(f"      [{i}] {c!r}")
        return chunks

    def send_file(self, data: str,
                  window_size: int = 4,
                  simulate_loss_at: int = 2) -> str:
        """
        Split data → TCP segments → Go-Back-N transfer.
        Returns the reassembled string as received by the GBN receiver.

        simulate_loss_at: sequence number to drop once (demonstrates
                          Go-Back-N retransmission).
        """
        chunks   = self.split(data)
        src_port = PortManager.allocate_ephemeral_port()

        segments = [
            TCPSegment(
                src_port = src_port,
                dst_port = self.PORT,
                seq_num  = i,
                ack_num  = 0,
                data     = chunk,
            )
            for i, chunk in enumerate(chunks)
        ]

        sender   = GoBackNSender(window_size=window_size)
        receiver = GoBackNReceiver()

        print(f"\n[FTP] Starting Go-Back-N transfer "
              f"(window={window_size}, loss at seq {simulate_loss_at})")

        received = sender.send(segments, receiver,
                               simulate_loss_at=simulate_loss_at)

        reassembled = "".join(str(d) for d in received)
        print(f"\n[FTP] Reassembled file : {reassembled!r}")
        return reassembled

    # ── Receiver side ─────────────────────────────────────────────────── #

    def on_receive(self, seq_num: int, data: str, from_ip: str):
        """Called by Node when a file-transfer segment arrives."""
        self._recv_chunks[seq_num] = data
        print(f"[FTP] {self.node.name} received chunk {seq_num}: {data!r} "
              f"from {from_ip}")

    def reassemble(self) -> str:
        result = "".join(self._recv_chunks[k]
                         for k in sorted(self._recv_chunks))
        print(f"[FTP] Reassembled ({len(self._recv_chunks)} chunks): {result!r}")
        return result
