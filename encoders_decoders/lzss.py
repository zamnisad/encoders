from .blockProcessor import *
import struct

class LZSS:
    def __init__(self, window_size=8192, block_size=4096):
        self.window_size = window_size
        self.block_size = block_size

    def encode(self, data: bytes) -> bytes:
        encoded = bytearray()

        for block in BlockProcessor.split_blocks(data, self.block_size):
            block_enc = bytearray(struct.pack('>I', self.window_size))
            i = 0

            while i < len(block):
                best = (0, 0)
                window_start = max(0, i - self.window_size)
                max_length = min(258, len(block) - i)

                for l in range(max_length, 0, -1):
                    substr = block[i:i + l]
                    pos = block.find(substr, window_start, i)
                    if pos != -1:
                        best = (i - pos - 1, l)
                        break

                if best[1] > 2:
                    packed = (best[0] << 12) | best[1]
                    block_enc.extend(b'\x01' + packed.to_bytes(3, 'big'))
                    i += best[1]
                else:
                    block_enc.extend(b'\x00' + block[i:i + 1])
                    i += 1

            encoded.extend(BlockProcessor.add_block_header(block_enc))

        return bytes(encoded)

    def decode(self, data: bytes) -> bytes:
        decoded = bytearray()
        ptr = 0

        while ptr < len(data):
            block_enc, ptr = BlockProcessor.read_block(data, ptr)
            if not block_enc:
                break

            window_size = struct.unpack('>I', block_enc[:4])[0]
            i = 4
            buf = bytearray()

            while i < len(block_enc):
                flag = block_enc[i]
                if flag == 0:
                    if i + 1 >= len(block_enc):
                        break
                    buf.append(block_enc[i + 1])
                    i += 2
                elif flag == 1:
                    if i + 4 > len(block_enc):
                        break
                    packed = int.from_bytes(block_enc[i + 1:i + 4], 'big')
                    offset = (packed >> 12) & 0xFFF
                    length = packed & 0xFFF
                    i += 4

                    length = max(3, length)
                    start = len(buf) - offset - 1
                    if start < 0 or start >= len(buf):
                        continue

                    for j in range(length):
                        if start + j >= len(buf):
                            break
                        buf.append(buf[start + j])
                else:
                    break

            decoded.extend(buf)

        return bytes(decoded)
