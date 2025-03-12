import os
import json
import time
import random
import string
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Type
from tqdm import tqdm

from encoders_decoders import (
    Huffman, RLE, BWT, MTF, LZSS, LZW
)
from generate.generate import (
    DataGenerator, ImageGenerator,
    TextGenerator, RawConverter
)


class CompressionAlgorithm:
    """Базовый класс для алгоритмов сжатия"""

    def __init__(self, block_size: int = 1024):
        self.block_size = block_size

    def encode(self, data: bytes) -> bytes:
        raise NotImplementedError

    def decode(self, data: bytes) -> bytes:
        raise NotImplementedError


class CompressionPipeline:
    """Класс для управления пайплайном сжатия"""
    COMPRESSORS: Dict[str, Tuple[Type[CompressionAlgorithm], ...]] = {
        "HA": (Huffman,),
        "RLE": (RLE,),
        "BWT+RLE": (BWT, RLE),
        "BWT+MTF+HA": (BWT, MTF, Huffman),
        "BWT+MTF+RLE+HA": (BWT, MTF, RLE, Huffman),
        "LZSS": (LZSS,),
        "LZSS+HA": (LZSS, Huffman),
        "LZW": (LZW,),
        "LZW+HA": (LZW, Huffman)
    }

    def __init__(self, encoder: str = 'BWT+MTF+RLE+HA', block_size: int = 1024):
        self.encoder = encoder
        self.block_size = block_size
        self.components = self._init_components()

    def _init_components(self) -> List[CompressionAlgorithm]:
        """Инициализация компонентов пайплайна"""
        return [cls(self.block_size) for cls in self.COMPRESSORS[self.encoder]]

    def encode(self, data: bytes) -> bytes:
        """Последовательное применение кодировщиков"""
        encoded = data
        for comp in self.components:
            encoded = comp.encode(encoded)
        return encoded

    def decode(self, data: bytes) -> bytes:
        """Последовательное применение декодеров (в обратном порядке)"""
        decoded = data
        for comp in reversed(self.components):
            decoded = comp.decode(decoded)
        return decoded


class FileProcessor:
    """Класс для работы с файловой системой"""

    @staticmethod
    def generate_name(length: int = 6) -> str:
        """Генерация случайного имени"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def prepare_test_environment() -> Path:
        """Подготовка тестового окружения"""
        test_dir = Path(__file__).parent.absolute() / "compression_test_data"
        test_dir.mkdir(exist_ok=True)

        DataGenerator.create_directory(str(test_dir))
        ImageGenerator.generate_images(str(test_dir))
        TextGenerator.generate_realistic_text(str(test_dir))
        RawConverter.convert_all_images(str(test_dir))

        return test_dir

    @classmethod
    def get_encoded_output_dir(cls) -> Path:
        """Создание выходной директории с именем: <random>_encoded"""
        base = Path.cwd()
        folder_name = cls.generate_name() + "_encoded"
        output_dir = base / folder_name
        output_dir.mkdir()
        return output_dir


class CompressionManager:
    """Основной класс для управления процессами сжатия"""

    def __init__(self):
        self.results: Dict[str, Tuple[int, int, float, float, float, float]] = {}

    def process_file(self, input_path: Path, encoder: str) -> Tuple[List[int], Path]:
        """
        Кодирует файл.
        Выходной файл имеет то же имя, что и исходный, и сохраняется в папке с именем <random>_encoded.
        Возвращает кортеж: (список размеров блоков, путь к папке с закодированным файлом)
        """
        pipeline = CompressionPipeline(encoder)
        output_dir = FileProcessor.get_encoded_output_dir()
        output_file = output_dir / input_path.name

        try:
            with open(input_path, 'rb') as f_in, open(output_file, 'wb') as f_out:
                metadata = json.dumps({'encoder': encoder}).encode()
                f_out.write(len(metadata).to_bytes(4, 'big'))
                f_out.write(metadata)

                while chunk := f_in.read(pipeline.block_size):
                    encoded = pipeline.encode(chunk)
                    f_out.write(encoded)

            block_count = (os.path.getsize(input_path) // pipeline.block_size) + 1
            return [pipeline.block_size] * block_count, output_dir

        except Exception as e:
            raise CompressionError(f"Ошибка обработки файла: {str(e)}")

    def benchmark(self, data: bytes) -> Dict[str, Tuple]:
        """
        In-memory benchmark для всех алгоритмов (файлы не создаются).
        """
        for name in tqdm(CompressionPipeline.COMPRESSORS.keys(), desc="Benchmarking"):
            try:
                pipeline = CompressionPipeline(name)

                start = time.perf_counter()
                encoded = pipeline.encode(data)
                enc_time = time.perf_counter() - start

                start = time.perf_counter()
                decoded = pipeline.decode(encoded)
                dec_time = time.perf_counter() - start

                assert decoded == data, "Декодирование не соответствует оригиналу"

                self.results[name] = (
                    len(data),
                    len(encoded),
                    len(encoded) / len(data),
                    enc_time,
                    dec_time,
                    enc_time + dec_time
                )

            except Exception as e:
                print(f"Ошибка в {name}: {str(e)}")
                self.results[name] = (0, 0, 0, 0, 0, 0)

        return self.results

    def print_benchmark_results(self):
        """Вывод результатов бенчмарка"""
        print("\n{:<25} | {:<10} | {:<10} | {:<10} | {:<10} | {:<10} | {:<10}".format(
            "Algorithm", "Input", "Output", "Ratio", "Enc Time", "Dec Time", "Total"))
        print("-" * 104)

        for name, (orig, comp, ratio, et, dt, tt) in self.results.items():
            print("{:<25} | {:>10} | {:>10} | {:>9.2%} | {:>10.5f} | {:>10.5f} | {:>10.5f}".format(
                name, f"{orig}B", f"{comp}B", ratio, et, dt, tt))

    def decode_file(self, encoded_dir: Path) -> Tuple[List[int], Path]:
        """
        Декодирует файл из указанной папки <random>_encoded.
        Результат сохраняется в папке с тем же именем, но со суффиксом "_decoded".
        Возвращает кортеж: (список размеров блоков, путь к папке с декодированным файлом)
        """
        encoded_files = list(encoded_dir.glob("*"))
        if not encoded_files:
            raise CompressionError("В указанной директории нет закодированного файла.")
        encoded_file = encoded_files[0]

        with open(encoded_file, 'rb') as f:
            meta_len_bytes = f.read(4)
            meta_len = int.from_bytes(meta_len_bytes, 'big')
            meta_json = f.read(meta_len)
            metadata = json.loads(meta_json)
            encoder = metadata.get("encoder")
            if encoder is None:
                raise CompressionError("В метаданных отсутствует информация о кодировщике.")
            encoded_data = f.read()

        pipeline = CompressionPipeline(encoder)
        decoded_data = pipeline.decode(encoded_data)

        decoded_dir_name = encoded_dir.name.replace("_encoded", "_decoded")
        decoded_dir = encoded_dir.parent / decoded_dir_name
        decoded_dir.mkdir(exist_ok=True)

        decoded_file = decoded_dir / encoded_file.name
        with open(decoded_file, 'wb') as f_out:
            f_out.write(decoded_data)

        block_count = (len(decoded_data) // pipeline.block_size) + 1
        return [pipeline.block_size] * block_count, decoded_dir

    def run_all_algorithms(self, input_path: Path):
        """
        Запускает кодирование и декодирование для каждого алгоритма из пайплайнов.
        После обработки временные папки удаляются.
        """
        with open(input_path, 'rb') as f:
            original_data = f.read()

        print(f"Запуск всех алгоритмов сжатия для файла '{input_path.name}'")
        for algorithm in CompressionPipeline.COMPRESSORS.keys():
            encoded_dir = None
            decoded_dir = None
            try:
                print(f"\nАлгоритм: {algorithm}")
                block_sizes_encoded, encoded_dir = self.process_file(input_path, algorithm)
                print(f"  Закодированная папка: {encoded_dir}")
                print(f"  Размер блоков при кодировании: {set(block_sizes_encoded)}")

                block_sizes_decoded, decoded_dir = self.decode_file(encoded_dir)
                print(f"  Декодированная папка: {decoded_dir}")
                print(f"  Размер блоков при декодировании: {set(block_sizes_decoded)}")

                decoded_files = list(decoded_dir.glob("*"))
                if decoded_files:
                    with open(decoded_files[0], 'rb') as f_dec:
                        decoded_data = f_dec.read()
                    if decoded_data == original_data:
                        print("  Результат: Успешно – декодированные данные совпадают с исходными.")
                    else:
                        print("  Результат: Ошибка – декодированные данные НЕ совпадают с исходными.")
                else:
                    print("  Результат: Ошибка – декодированный файл не найден.")
            except Exception as e:
                print(f"  Ошибка при обработке алгоритма {algorithm}: {e}")
            finally:
                if encoded_dir and encoded_dir.exists():
                    try:
                        shutil.rmtree(encoded_dir)
                        print(f"  Удалена папка: {encoded_dir}")
                    except Exception as e:
                        print(f"  Ошибка при удалении папки {encoded_dir}: {e}")
                if decoded_dir and decoded_dir.exists():
                    try:
                        shutil.rmtree(decoded_dir)
                        print(f"  Удалена папка: {decoded_dir}")
                    except Exception as e:
                        print(f"  Ошибка при удалении папки {decoded_dir}: {e}")


class CompressionError(Exception):
    pass


if __name__ == "__main__":
    enwik7_path = Path("./compression_test_data/real_text.txt")
    if not enwik7_path.exists():
        print("Файл enwik7 не найден!")
        exit(1)

    manager = CompressionManager()
    with open(enwik7_path, 'rb') as f:
        data = f.read()
    manager.benchmark(data)
    manager.print_benchmark_results()

    manager.run_all_algorithms(enwik7_path)