from .blockProcessor import *

class _Sorting:
    def __init__(self):
        pass

    def sort(self, arr):
        if len(arr) <= 1:
            return arr

        first, middle, last = arr[0], arr[len(arr) // 2], arr[-1]
        pivot = sorted([first, middle, last])[1]

        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]

        return self.sort(left) + middle + self.sort(right)


class BWT:
    def __init__(self, block_size=1024):
        self.block_size = block_size

    def encode(self, data: bytes) -> bytes:
        data = data.lstrip(b'\x00')

        encoded = bytearray()
        for block in BlockProcessor.split_blocks(data, self.block_size):
            if not block:
                continue

            rotations = [block[i:] + block[:i] for i in range(len(block))]
            sa = _Sorting().sort(rotations)
            last_col = bytes(rotations[i][-1] for i in sa)
            orig_idx = sa.index(0)

            encoded_block = struct.pack('>II', orig_idx, len(block)) + last_col
            encoded.extend(BlockProcessor.add_block_header(encoded_block))

        return bytes(encoded)

    def decode(self, data: bytes) -> bytes:
        decoded = bytearray()
        ptr = 0

        while ptr <= len(data):
            block, ptr = BlockProcessor.read_block(data, ptr)
            if not block:
                break

            if len(block) < 8:
                continue

            try:
                orig_idx, blen = struct.unpack('>II', block[:8])
            except struct.error:
                continue

            last_col = block[8:8 + blen]

            if len(last_col) != blen:
                continue

            tuples = [(last_col[i], i) for i in range(blen)]
            sorted_tuples = sorted(tuples, key=lambda x: (x[0], x[1]))
            LF = [t[1] for t in sorted_tuples]
            first_col = [t[0] for t in sorted_tuples]

            current_idx = orig_idx
            result = bytearray()
            for _ in range(blen):
                result.append(first_col[current_idx])
                current_idx = LF[current_idx]

            decoded.extend(result)

        return bytes(decoded).lstrip(b'\x00')