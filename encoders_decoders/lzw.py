from .blockProcessor import *


class LZW:
    def __init__(self, block_size=4096):
        self.block_size = block_size
        self.reset_dict()

    def reset_dict(self):
        self.dict_size = 256
        self.dictionary = {bytes([i]): i for i in range(256)}
        self.rev_dict = {i: bytes([i]) for i in range(256)}

    def encode(self, data: bytes) -> bytes:
        encoded = bytearray()

        for block in BlockProcessor.split_blocks(data, self.block_size):
            self.reset_dict()
            w = b''
            block_enc = bytearray()

            for c in block:
                wc = w + bytes([c])
                if wc in self.dictionary:
                    w = wc
                else:
                    block_enc.extend(struct.pack('>H', self.dictionary[w]))
                    self.dictionary[wc] = self.dict_size
                    self.dict_size += 1
                    w = bytes([c])

            if w:
                block_enc.extend(struct.pack('>H', self.dictionary[w]))

            encoded.extend(BlockProcessor.add_block_header(block_enc))

        return bytes(encoded)

    def decode(self, data: bytes) -> bytes:
        decoded = bytearray()
        ptr = 0

        while ptr < len(data):
            block_enc, ptr = BlockProcessor.read_block(data, ptr)
            if not block_enc:
                break

            self.reset_dict()
            idx = 0

            if len(block_enc) < 2:
                continue  # Пропустить неполные данные

            # Обработка первого кода
            code = struct.unpack('>H', block_enc[idx:idx+2])[0]
            idx += 2
            if code not in self.rev_dict:
                continue
            prev = self.rev_dict[code]
            decoded.extend(prev)

            # Обработка оставшихся кодов
            while idx < len(block_enc):
                if idx + 2 > len(block_enc):
                    break
                code = struct.unpack('>H', block_enc[idx:idx+2])[0]
                idx += 2

                if code in self.rev_dict:
                    entry = self.rev_dict[code]
                elif code == self.dict_size:
                    entry = prev + prev[0:1]
                else:
                    break  # Некорректный код

                decoded.extend(entry)
                self.rev_dict[self.dict_size] = prev + entry[0:1]
                self.dict_size += 1
                prev = entry

        return bytes(decoded)