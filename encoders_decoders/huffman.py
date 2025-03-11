from .blockProcessor import *
from collections import defaultdict
from heapq import heappop, heapify, heappush


class Huffman:
    def __init__(self, block_size=4096):
        self.block_size = block_size

    def encode(self, data: bytes) -> bytes:
        encoded = bytearray()

        for block in BlockProcessor.split_blocks(data, self.block_size):
            freq = defaultdict(int)
            for b in block:
                freq[b] += 1

            heap = [[wt, [sym, ""]] for sym, wt in freq.items()]
            heapify(heap)

            while len(heap) > 1:
                lo = heappop(heap)
                hi = heappop(heap)
                for pair in lo[1:]:
                    pair[1] = '0' + pair[1]
                for pair in hi[1:]:
                    pair[1] = '1' + pair[1]
                heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

            codes = {sym: code for sym, code in heap[0][1:]}
            bit_str = ''.join(codes[b] for b in block)
            padding = (8 - (len(bit_str) % 8) % 8)
            bit_str += '0' * padding
            header = struct.pack('>BH', padding, len(freq))
            for sym, count in freq.items():
                header += struct.pack('>BI', sym, count)

            block_enc = bytearray()
            for i in range(0, len(bit_str), 8):
                block_enc.append(int(bit_str[i:i + 8], 2))

            encoded.extend(BlockProcessor.add_block_header(header + block_enc))

        return bytes(encoded)

    def decode(self, data: bytes) -> bytes:
        decoded = bytearray()
        ptr = 0

        while ptr < len(data):
            block, ptr = BlockProcessor.read_block(data, ptr)
            if not block:
                break

            padding = block[0]
            num_syms = struct.unpack('>H', block[1:3])[0]
            freq = {}
            pos = 3

            for _ in range(num_syms):
                sym = block[pos]
                count = struct.unpack('>I', block[pos + 1:pos + 5])[0]
                freq[sym] = count
                pos += 5

            heap = [[wt, [sym, ""]] for sym, wt in freq.items()]
            heapify(heap)

            while len(heap) > 1:
                lo = heappop(heap)
                hi = heappop(heap)
                for pair in lo[1:]:
                    pair[1] = '0' + pair[1]
                for pair in hi[1:]:
                    pair[1] = '1' + pair[1]
                heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

            codes = {sym: code for sym, code in heap[0][1:]}
            rev_codes = {v: k for k, v in codes.items()}

            bit_str = ''.join(f'{b:08b}' for b in block[pos:])
            bit_str = bit_str[:-padding] if padding else bit_str

            current = ''
            for bit in bit_str:
                current += bit
                if current in rev_codes:
                    decoded.append(rev_codes[current])
                    current = ''

        return bytes(decoded)