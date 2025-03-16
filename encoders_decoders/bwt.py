from .blockProcessor import *

class _Sorting:
    def __init__(self):
        pass

    def sort_indices(self, rotations):
        indices = list(range(len(rotations)))
        return self.merge_sort(rotations, indices)

    def merge_sort(self, rotations, indices):
        if len(indices) <= 1:
            return indices
        mid = len(indices) // 2
        left = self.merge_sort(rotations, indices[:mid])
        right = self.merge_sort(rotations, indices[mid:])
        return self.merge(rotations, left, right)

    def merge(self, rotations, left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            # При равных ротациях сравниваем исходные индексы
            if (rotations[left[i]] < rotations[right[j]] or
                    (rotations[left[i]] == rotations[right[j]] and left[i] < right[j])):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result


class BWT:
    def __init__(self, block_size):
        self.block_size = block_size

    def encode(self, data: bytes) -> bytes:

        encoded = bytearray()
        for block in BlockProcessor.split_blocks(data, self.block_size):
            if not block:
                continue

            rotations = [block[i:] + block[:i] for i in range(len(block))]
            sa = _Sorting().sort_indices(rotations)
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

            # Создаём пары (символ, индекс) и выполняем стабильную сортировку
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

        return bytes(decoded)