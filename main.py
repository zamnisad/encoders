from pathlib import Path
from generate.generate import *
from encoders_decoders.imports import *
from typing import Dict
from tqdm import tqdm
import time


def setup_test_environment():
    current_dir = Path(__file__).parent.absolute()

    test_data_dir = current_dir / "compression_test_data"

    test_data_dir.mkdir(exist_ok=True)

    DataGenerator.create_directory(str(test_data_dir))
    ImageGenerator.generate_images(str(test_data_dir))
    TextGenerator.generate_realistic_text(str(test_data_dir))
    RawConverter.convert_all_images(str(test_data_dir))

    print(f"Тестовые данные созданы в: {test_data_dir}")
    return test_data_dir


def run_compressors(data: bytes, results: Dict) -> None:
    """Запуск всех компрессоров с замером метрик"""
    compressors = {
        "HA": lambda: Huffman(),
        "RLE": lambda: RLE(),
        "BWT+RLE": lambda: (BWT(), RLE()),
        "BWT+MTF+HA": lambda: (BWT(), MTF(), Huffman()),
        "BWT+MTF+RLE+HA": lambda: (BWT(), MTF(), RLE(), Huffman()),
        "LZSS": lambda: LZSS(),
        "LZSS+HA": lambda: (LZSS(), Huffman()),
        "LZW": lambda: LZW(),
        "LZW+HA": lambda: (LZW(), Huffman())
    }

    for name, init_fn in tqdm(compressors.items(), 'Compressors: '):
        components = init_fn()
        if not isinstance(components, tuple):
            components = (components,)

        try:
            start_enc = time.perf_counter()
            encoded = data
            for c in components:
                encoded = c.encode(encoded)
            enc_time = time.perf_counter() - start_enc

            start_dec = time.perf_counter()
            decoded = encoded
            for c in reversed(components):
                decoded = c.decode(decoded)
            dec_time = time.perf_counter() - start_dec

            assert decoded == data
            ratio = len(encoded) / len(data)
            total_time = enc_time + dec_time

            results[name] = (len(data), len(encoded), ratio, enc_time, dec_time, total_time)

        except Exception as e:
            print(f"Ошибка в {name}: {str(e)}")
            results[name] = (len(data), 0, 0, 0, 0, 0)


def print_results(results: Dict):
    """Вывод результатов в табличном виде"""
    print("\n{:<25} | {:<10} | {:<10} | {:<10} | {:<10} | {:<10} | {:<10}".format(
        "Compressor", "Original", "Compressed", "Ratio", "Enc Time", "Dec Time", "Total Time"))
    print("-" * 104)

    for name, (original, compressed, ratio, et, dt, tt) in results.items():
        print("{:<25} | {:>10} | {:>10} | {:>10.3f} | {:>10.5f} | {:>10.5f} | {:>10.5f}".format(
            name,
            f"{original} B",
            f"{compressed} B",
            ratio,
            et,
            dt,
            tt
        ))


# Пример использования
if __name__ == "__main__":
    link = './compression_test_data/enwik7'

    with open(link, 'rb') as f:
        b_data = f.read()

    print(len(b_data) / 1024)
    results = {}

    run_compressors(b_data, results)

    print_results(results)