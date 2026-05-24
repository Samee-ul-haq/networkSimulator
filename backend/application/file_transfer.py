class FileTransferApp:

    def __init__(self,
                 chunk_size=5):
        self.chunk_size = chunk_size

    def split_file(self, data):
        chunks = []
        for i in range(
            0,
            len(data),
            self.chunk_size
        ):

            chunks.append(
                data[i:i+self.chunk_size]
            )

        return chunks