from .blockProcessor import *
import struct

"""
Update:
    1) (12, 12) -> (15, 9), [(offset, len)]
    2) флаг исправлен, теперь вместо дополнительного флага в виде байта используется битовый флаг
    3) find и вложенный цикл заменен на словарь, который хранит список позиций, где уже была эта последовательность
    4) Ограничение совпадения до 511 бит (9 байт)
"""

class LZSS:
    def __init__(self, block_size, window_size=2048):
        self.window_size = window_size
        self.block_size = block_size

    def encode(self, data: bytes) -> bytes:
        bp = BlockProcessor()
        encoded = bytearray()

        for block in bp.split_blocks(data, self.block_size):
            block_enc = bytearray(struct.pack('>I', self.window_size))
            i = 0
            pos_dict = {}
            while i < len(block):
                flag = 0
                tokens = bytearray()
                token_count = 0
                while token_count < 8 and i < len(block):
                    window_start = max(0, i - self.window_size)
                    best_length = 0
                    best_offset = 0

                    if i < len(block) - 1:
                        key = block[i:i + 2]
                        if key in pos_dict:
                            for candidate in pos_dict[key]:
                                if candidate < window_start:
                                    continue
                                length = 0
                                while (i + length < len(block) and
                                       candidate + length < len(block) and
                                       block[candidate + length] == block[i + length]):
                                    length += 1
                                    if length >= min(511, len(block) - i):
                                        break
                                if length > best_length:
                                    best_length = length
                                    best_offset = i - candidate
                                    if best_length == min(511, len(block) - i):
                                        break

                    if best_length >= 3:
                        ref = (best_offset << 9) | best_length
                        tokens.extend(ref.to_bytes(3, 'big'))
                        flag |= (1 << token_count)
                        # Обновляем словарь для всех позиций, покрытых ссылкой
                        for j in range(best_length):
                            if i + j < len(block) - 1:
                                key = block[i + j:i + j + 2]
                                pos_dict.setdefault(key, []).append(i + j)
                        i += best_length
                    else:
                        # Литерал – записываем один байт
                        tokens.append(block[i])
                        if i < len(block) - 1:
                            key = block[i:i + 2]
                            pos_dict.setdefault(key, []).append(i)
                        i += 1

                    token_count += 1

                block_enc.append(flag)
                block_enc.extend(tokens)
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

            _ = struct.unpack('>I', block_enc[:4])[0]
            i = 4
            buf = bytearray()

            while i < len(block_enc):
                flag = block_enc[i]
                i += 1
                for bit in range(8):
                    if i >= len(block_enc):
                        break
                    if flag & (1 << bit):
                        if i + 3 > len(block_enc):
                            break
                        ref = int.from_bytes(block_enc[i:i+3], 'big')
                        i += 3
                        offset = ref >> 9
                        length = ref & 0x1FF
                        if length < 3:
                            length = 3
                        start = len(buf) - offset
                        for j in range(length):
                            if start + j < 0 or start + j >= len(buf):
                                break
                            buf.append(buf[start + j])
                    else:
                        buf.append(block_enc[i])
                        i += 1
            decoded.extend(buf)
        return bytes(decoded)