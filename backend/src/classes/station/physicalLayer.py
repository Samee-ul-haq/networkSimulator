import time
import random

class senderSidePhysical:
    def __init__(self, device):
        self.device = device
        self.k = 0            

    def transmitToMedium(self, bits_string, medium):
        if self.device.port is None:
            print(f"[PHY SENDER] {self.device.name} has no port assigned.")
            return

        self.k = 0

        while self.k <= 15:
            # ── Step 1: Carrier Sense ─────────────────────────────────
            while medium.is_busy():
                print(f"[PHY SENDER] {self.device.name} sensing medium busy, waiting...")
                time.sleep(0.1)

            # ── Step 2: Start transmitting ────────────────────────────
            medium.transmitters.add(self.device)
            print(f"[PHY SENDER] {self.device.name} started transmitting "
                  f"(attempt {self.k + 1})")

            collision_occurred = False

            for bit in bits_string:
                # ── Step 3: Collision Detection ───────────────────────
                if medium.collision():
                    collision_occurred = True
                    break
                medium.transmit(self.device.port, bit=bit, flag=True)
                time.sleep(0.001)          # Reduced from 1s for simulation speed

            if not collision_occurred:
                # ── Step 5: Transmission successful ───────────────────
                medium.transmitters.discard(self.device)
                medium.transmit(self.device.port, completion=True)
                print(f"[PHY SENDER] {self.device.name} transmission complete.")
                self.k = 0               # Reset backoff counter for next send
                return

            else:
                # ── Step 4: Collision — jam + backoff ─────────────────
                print(f"[PHY SENDER] {self.device.name} collision detected!")
                medium.transmit(self.device.port)   # Jam signal (no flags = collision)
                medium.transmitters.discard(self.device)

                self.k += 1
                if self.k > 15:
                    print(f"[PHY SENDER] {self.device.name} max retries reached. Aborting.")
                    return

                Tfr = len(bits_string)
                backoff = random.randint(0, 2**self.k - 1) * Tfr * 0.001
                print(f"[PHY SENDER] {self.device.name} backing off for "
                      f"{backoff:.3f}s (k={self.k})")
                time.sleep(backoff)


class recieverSidePhysical:
    def __init__(self, device):
        self.device = device
        self.tray = []               # Accumulates bits until transfer() is called

    def recieve_bit(self, bit):      # Called by medium for each bit
        self.tray.append(bit)

    def collision_detected(self):    # Called by medium on jam signal
        print(f"[PHY RECV] {self.device.name} collision signal received, clearing tray.")
        self.tray.clear()

    def transfer(self):              # Called by medium on completion signal
        if not self.tray:
            return
        bit_string = "".join(self.tray)
        self.tray.clear()
        print(f"[PHY RECV] {self.device.name} received {len(bit_string)} bits, "
              f"passing to Data Link layer.")
        # Pass bits up to receiver data link layer
        self.device.recieverSideDataLink.receive(bit_string)
