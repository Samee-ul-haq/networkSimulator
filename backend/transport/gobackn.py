class GoBackNSender:

    def __init__(self,
                 sender_node,
                 receiver_ip,
                 gateway,
                 source_port,
                 destination_port,
                 window_size=4):

        self.sender_node = sender_node
        self.receiver_ip = receiver_ip
        self.gateway = gateway
        self.source_port = source_port
        self.destination_port = destination_port
        self.window_size = window_size
        self.base = 0
        self.next_seq_num = 0
        self.loss_simulated = False

    def send(self, chunks):
        print("\n[GO-BACK-N PROTOCOL]\n")
        while self.base < len(chunks):
            while (
                self.next_seq_num < self.base + self.window_size
                and
                self.next_seq_num < len(chunks)
            ):

                chunk = chunks[self.next_seq_num]

                print(
                    f"\nSending Segment "
                    f"{self.next_seq_num}"
                )

                self.sender_node.send_data(
                    destination_ip=self.receiver_ip,
                    message=chunk,
                    gateway=self.gateway,
                    source_port=self.source_port,
                    destination_port=self.destination_port,
                    sequence_number=self.next_seq_num
                )

                self.next_seq_num += 1
            ack = self.receive_ack()
            if ack is None:

                print("\nTimeout occurred")

                print(
                    f"Retransmitting from "
                    f"segment {self.base}"
                )
                self.next_seq_num = self.base

            else:
                print(
                    f"\nACK received : {ack}"
                )

                self.base = ack + 1

    def receive_ack(self):

        """
        Simulate one packet loss.
        """

        if self.base == 2 and not self.loss_simulated:
            self.loss_simulated = True
            return None

        return self.base