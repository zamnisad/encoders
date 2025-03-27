import matplotlib.pyplot as plt
from pathlib import Path

from encoders_decoders import LZSS


def compress_lzss(data: bytes, buffer_size: int) -> bytes:
    """
    Сжимает данные с использованием алгоритма LZSS с заданным размером буфера.
    Предполагается, что конструктор LZSS принимает размер буфера как параметр.
    """
    lzss = LZSS(4096, window_size=buffer_size)
    return lzss.encode(data)


def main():
    # Путь к файлу enwik7 (при необходимости измените путь)
    file_path = Path("Z:\prog\аисдик\compression_test_data\enwik7")
    if not file_path.exists():
        print("Файл enwik7 не найден!")
        return

    with open(file_path, "rb") as f:
        data = f.read()
    original_size = len(data)

    buffer_sizes = [128, 256, 512, 1024, 2048, 4096, 8192]
    compression_ratios = []

    for bs in buffer_sizes:
        compressed_data = compress_lzss(data, bs)
        compressed_size = len(compressed_data)
        ratio = original_size / compressed_size
        compression_ratios.append(ratio)
        print(f"Размер буфера: {bs} байт, Коэффициент сжатия: {ratio:.4f}")

    plt.figure(figsize=(8, 6))
    plt.plot(buffer_sizes, compression_ratios, marker="o")
    plt.xlabel("Размер буфера (байт)")
    plt.ylabel("Коэффициент сжатия (исходный/сжатый)")
    plt.title("Зависимость коэффициента сжатия от размера буфера (LZSS) для enwik7")
    plt.grid(True)
    plt.savefig("compression_ratio_vs_buffer_size.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
