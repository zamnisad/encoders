from .blockProcessor import *


class RLE:
    def __init__(self, block_size=8192):
        self.block_size = block_size

    def encode(self, data: bytes) -> bytes:
        encoded = bytearray()

        for block in BlockProcessor.split_blocks(data, self.block_size):
            block_enc = bytearray()
            prev = block[0] if block else 0
            count = 1

            for b in block[1:]:
                if b == prev and count < 255:
                    count += 1
                else:
                    block_enc.extend([count, prev])
                    prev = b
                    count = 1

            if count > 0:
                block_enc.extend([count, prev])

            encoded.extend(BlockProcessor.add_block_header(block_enc))

        return bytes(encoded)

    def decode(self, data: bytes) -> bytes:
        decoded = bytearray()
        ptr = 0

        while ptr < len(data):
            block_enc, ptr = BlockProcessor.read_block(data, ptr)
            if not block_enc:
                break

            for i in range(0, len(block_enc), 2):
                count, byte = block_enc[i], block_enc[i + 1]
                decoded.extend([byte] * count)

        return bytes(decoded)