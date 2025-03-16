from .blockProcessor import *


class MTF:
    def __init__(self, block_size):
        self.block_size = block_size

    def encode(self, data: bytes) -> bytes:
        bp = BlockProcessor()

        encoded = bytearray()
        symbols = list(range(256))
        for block in bp.split_blocks(data, self.block_size):
            block_enc = bytearray()
            local_symbols = symbols.copy()

            for b in block:
                idx = local_symbols.index(b)
                block_enc.append(idx)
                del local_symbols[idx]
                local_symbols.insert(0, b)

            encoded.extend(bp.add_block_header(block_enc))

        return bytes(encoded)

    def decode(self, data: bytes) -> bytes:
        bp = BlockProcessor()

        decoded = bytearray()
        ptr = 0

        while ptr < len(data):
            block_enc, ptr = bp.read_block(data, ptr)
            if not block_enc:
                break

            symbols = list(range(256))
            for idx in block_enc:
                b = symbols[idx]
                decoded.append(b)
                del symbols[idx]
                symbols.insert(0, b)

        return bytes(decoded)