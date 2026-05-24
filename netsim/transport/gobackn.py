"""
Transport Layer — Go-Back-N ARQ (RFC 793 sliding window).

Sender
------
  Maintains a window of up to N unacknowledged segments.
  On timeout or NACK: retransmits all segments from base of window.

Receiver
--------
  Accepts only in-order segments.
  Out-of-order segments are discarded; last good ACK is repeated.
  Simulates packet loss at a configurable sequence number.
"""


class GoBackNReceiver:
    def __init__(self):
        self.expected_seq      = 0
        self.received_segments = []
        self._loss_done        = set()   # seqs already simulated-lost

    def receive(self, segment, simulate_loss_at: int = None) -> int:
        """
        Process one arriving segment.
        Returns:
          seq_num  — ACK for the accepted segment.
          -1       — segment lost (no ACK sent).
          expected_seq - 1  — out-of-order (repeat last ACK).
        """
        seq = segment.seq_num

        # ── Simulate packet loss ──────────────────────────────────────
        if (simulate_loss_at is not None and
                seq == simulate_loss_at and
                seq not in self._loss_done):
            self._loss_done.add(seq)
            print(f"  [GBN RECV] ✗ Segment {seq} LOST (simulated drop)")
            return -1   # no ACK

        # ── In-order delivery ─────────────────────────────────────────
        if seq == self.expected_seq:
            self.received_segments.append(segment)
            self.expected_seq += 1
            print(f"  [GBN RECV] ✓ Segment {seq} OK → ACK {seq}")
            return seq

        # ── Out-of-order: discard, repeat last ACK ────────────────────
        last_ack = self.expected_seq - 1
        print(f"  [GBN RECV] ✗ Out-of-order: expected {self.expected_seq}, "
              f"got {seq} → repeat ACK {last_ack}")
        return last_ack

    def all_data(self) -> list:
        return [seg.data for seg in self.received_segments]

    def reassemble(self) -> str:
        return "".join(str(d) for d in self.all_data())


class GoBackNSender:
    def __init__(self, window_size: int = 4):
        self.window_size = window_size
        self.base        = 0
        self.next_seq    = 0

    def send(self, segments: list,
             receiver: GoBackNReceiver,
             simulate_loss_at: int = None) -> list:
        """
        Transmit all segments to receiver using Go-Back-N.
        Returns list of received data chunks in order.

        simulate_loss_at : sequence number to drop once (for demonstration).
        """
        total = len(segments)
        print(f"\n[GBN] Window size = {self.window_size} | "
              f"Total segments = {total}"
              + (f" | Loss simulated at seq {simulate_loss_at}"
                 if simulate_loss_at is not None else ""))

        while self.base < total:
            # ── Send window ───────────────────────────────────────────
            while (self.next_seq < self.base + self.window_size and
                   self.next_seq < total):
                seg = segments[self.next_seq]
                print(f"\n[GBN SEND] Window [{self.base}–"
                      f"{min(self.base+self.window_size-1, total-1)}] "
                      f"| Sending segment {self.next_seq}")
                seg.show()

                ack = receiver.receive(seg, simulate_loss_at=simulate_loss_at)

                if ack == -1:
                    # Packet lost → timeout → retransmit from base
                    print(f"\n[GBN SEND] ⏱ Timeout! No ACK received.")
                    print(f"[GBN SEND] Retransmitting from segment {self.base}")
                    self.next_seq = self.base
                    break   # restart inner loop from base

                # Cumulative ACK: slide window
                print(f"[GBN SEND] ← ACK {ack} received | "
                      f"Sliding window to {ack + 1}")
                self.base     = ack + 1
                self.next_seq = max(self.next_seq, ack + 1)

        print(f"\n[GBN] ✓ All {total} segments delivered and acknowledged.")
        return receiver.all_data()
