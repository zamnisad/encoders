import os
import json
import shutil
import string
import tempfile
import unittest
from pathlib import Path
from io import StringIO
import sys
from unittest.mock import patch

# Предполагаем, что основной код находится в модуле compression.py
from main import (
    CompressionAlgorithm,
    CompressionPipeline,
    FileProcessor,
    CompressionManager,
    CompressionError
)

# Тесты для CompressionPipeline
class TestCompressionPipeline(unittest.TestCase):
    def test_encode_decode_identity(self):
        """Проверяем, что для всех комбинаций алгоритмов
        сжатие/распаковка не искажают данные."""
        data = b"Hello world! This is a test. 1234567890" * 3
        for encoder in CompressionPipeline.COMPRESSORS.keys():
            with self.subTest(encoder=encoder):
                pipeline = CompressionPipeline(encoder, block_size=16)
                encoded = pipeline.encode(data)
                decoded = pipeline.decode(encoded)
                self.assertEqual(decoded, data, f"Ошибка для пайплайна {encoder}")

# Тесты для FileProcessor
class TestFileProcessor(unittest.TestCase):
    def test_generate_name(self):
        """Проверяем, что сгенерированное имя имеет требуемую длину и состоит из допустимых символов."""
        name = FileProcessor.generate_name()
        self.assertEqual(len(name), 6)
        self.assertTrue(all(c in string.ascii_letters + string.digits for c in name))

    def test_get_unique_output_dir(self):
        """Проверяем, что метод возвращает уникальную директорию."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                output_dir = FileProcessor.get_unique_output_dir()
                self.assertTrue(output_dir.exists() and output_dir.is_dir())
                # Создаём ещё одну директорию и убеждаемся, что они различны
                output_dir2 = FileProcessor.get_unique_output_dir()
                self.assertNotEqual(output_dir, output_dir2)
            finally:
                os.chdir(original_cwd)

    def test_prepare_test_environment(self):
        """
        Проверяем, что тестовое окружение создаётся корректно.
        Вместо патчинга FileProcessor.__globals__, патчим переменную __file__
        в модуле, чтобы метод определял путь относительно поддельного файла.
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            fake_file = Path(tmpdirname) / "fake_module.py"
            fake_file.touch()
            # Патчим __file__ в модуле compression, чтобы FileProcessor.prepare_test_environment
            # использовал нужное значение
            with patch('main.__file__', fake_file.as_posix()):
                with patch("main.DataGenerator.create_directory") as mock_create_dir, \
                     patch("main.ImageGenerator.generate_images") as mock_generate_images, \
                     patch("main.TextGenerator.generate_realistic_text") as mock_generate_text, \
                     patch("main.RawConverter.convert_all_images") as mock_convert_images:
                    env_path = FileProcessor.prepare_test_environment()
                    self.assertTrue(env_path.exists() and env_path.is_dir())
                    # Очистка созданной тестовой директории
                    shutil.rmtree(env_path, ignore_errors=True)

# Тесты для CompressionManager
class TestCompressionManager(unittest.TestCase):
    def test_benchmark(self):
        """Проверяем, что benchmark возвращает словарь с корректной структурой результатов."""
        sample_data = b"Benchmark test data " * 50
        manager = CompressionManager()
        results = manager.benchmark(sample_data)
        self.assertEqual(set(results.keys()), set(CompressionPipeline.COMPRESSORS.keys()))
        for key, value in results.items():
            self.assertEqual(len(value), 6)
            self.assertIsInstance(value[0], int)
            self.assertIsInstance(value[1], int)
            self.assertIsInstance(value[2], float)
            self.assertIsInstance(value[3], float)
            self.assertIsInstance(value[4], float)
            self.assertIsInstance(value[5], float)
            self.assertEqual(value[0], len(sample_data))

    def test_print_benchmark_results(self):
        """Проверяем, что метод печатает результаты бенчмарка (захватываем stdout)."""
        sample_data = b"Benchmark test data " * 50
        manager = CompressionManager()
        manager.benchmark(sample_data)
        captured_output = StringIO()
        original_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            manager.print_benchmark_results()
        finally:
            sys.stdout = original_stdout
        output = captured_output.getvalue()
        self.assertIn("Algorithm", output)
        self.assertIn("Input", output)
        self.assertIn("Output", output)

    def test_process_file(self):
        """Проверяем корректность работы process_file:
        - проверяем запись метаданных в выходном файле,
        - возвращается правильное количество блоков.
        """
        sample_data = b"Test data for process file" * 10
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(sample_data)
            tmp_file_path = Path(tmp_file.name)
        try:
            with tempfile.TemporaryDirectory() as tmp_output_dir:
                with patch.object(FileProcessor, 'get_unique_output_dir', return_value=Path(tmp_output_dir)):
                    manager = CompressionManager()
                    block_sizes = manager.process_file(tmp_file_path, 'BWT+MTF+RLE+HA')
                    expected_blocks = (len(sample_data) // 1024) + 1
                    self.assertEqual(len(block_sizes), expected_blocks)
                    output_files = list(Path(tmp_output_dir).iterdir())
                    self.assertTrue(len(output_files) > 0)
                    with open(output_files[0], 'rb') as f:
                        meta_len_bytes = f.read(4)
                        meta_len = int.from_bytes(meta_len_bytes, 'big')
                        meta_json = f.read(meta_len)
                        metadata = json.loads(meta_json)
                        self.assertEqual(metadata, {'encoder': 'BWT+MTF+RLE+HA'})
        finally:
            tmp_file_path.unlink()

    def test_process_file_error(self):
        """Проверяем, что при попытке обработки несуществующего файла генерируется CompressionError."""
        manager = CompressionManager()
        invalid_path = Path("non_existent_file.txt")
        with self.assertRaises(CompressionError):
            manager.process_file(invalid_path, 'BWT+MTF+RLE+HA')

if __name__ == "__main__":
    unittest.main()
