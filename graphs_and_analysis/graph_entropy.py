import math
import matplotlib.pyplot as plt
from pathlib import Path

from encoders_decoders import BWT, MTF


def compute_entropy(data: bytes) -> float:
    """
    Вычисляет энтропию (в битах на символ) для заданных данных.
    """
    if not data:
        return 0.0
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    total = len(data)
    entropy = 0.0
    for count in freq.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def bwt_mtf_encode(data: bytes, block_size: int) -> bytes:
    """
    Применяет последовательность преобразований BWT и MTF для данных,
    разбитых на блоки указанного размера.
    Каждый блок обрабатывается независимо.
    """
    result = b""
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        bwt = BWT(block_size)
        mtf = MTF(block_size)
        encoded_block = mtf.encode(bwt.encode(block))
        result += encoded_block
    return result


def main():
    # Путь к файлу enwik7 (при необходимости измените путь)
    file_path = Path("Z:\prog\аисдик\compression_test_data\enwik7")
    if not file_path.exists():
        print("Файл enwik7 не найден!")
        return

    with open(file_path, "rb") as f:
        data = f.read()

    block_sizes = [256, 512, 1024, 2048, 4096, 8192]
    entropies = []

    for bs in block_sizes:
        encoded_data = bwt_mtf_encode(data, bs)
        entropy_value = compute_entropy(encoded_data)
        entropies.append(entropy_value)
        print(f"Размер блока: {bs} байт, Энтропия: {entropy_value:.4f} бит/символ")

    plt.figure(figsize=(8, 6))
    plt.plot(block_sizes, entropies, marker="o")
    plt.xlabel("Размер блока (байт)")
    plt.ylabel("Энтропия (бит/символ)")
    plt.title("Зависимость энтропии от размера блока (BWT+MTF) для enwik7")
    plt.grid(True)
    plt.savefig("entropy_vs_block_size.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
