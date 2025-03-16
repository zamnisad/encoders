import struct

class BlockProcessor:
    BLOCK_HEADER = struct.Struct('>I')
    use_header = True

    @classmethod
    def split_blocks(cls, data: bytes, block_size: int) -> list:
        if cls.use_header:
            return [data[i:i + block_size] for i in range(0, len(data), block_size)]
        else:
            return [data]

    @classmethod
    def add_block_header(cls, block: bytes) -> bytes:
        if cls.use_header:
            return cls.BLOCK_HEADER.pack(len(block)) + block
        else:
            return block

    @classmethod
    def read_block(cls, data: bytes, ptr: int) -> tuple:
        if cls.use_header:
            if ptr + cls.BLOCK_HEADER.size > len(data):
                return None, ptr
            block_len = cls.BLOCK_HEADER.unpack_from(data, ptr)[0]
            ptr += cls.BLOCK_HEADER.size
            return data[ptr:ptr + block_len], ptr + block_len
        else:
            return data[ptr:], len(data)
