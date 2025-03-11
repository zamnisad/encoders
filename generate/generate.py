import os
import numpy as np
from PIL import Image
import random


def convert_to_raw(image_path, output_path, image_type):
    img = Image.open(image_path)
    img = img.convert('L' if image_type == 'gray' else 'RGB')
    pixels = np.array(img)

    with open(output_path, 'wb') as f:
        if image_type == 'bw':
            f.write(b'BW')
            f.write(pixels.tobytes())
        elif image_type == 'gray':
            f.write(b'GR')
            f.write(pixels.tobytes())
        elif image_type == 'color':
            f.write(b'CL')
            f.write(pixels.tobytes())


class DataGenerator:
    @staticmethod
    def create_directory(path='test_data'):
        if not os.path.exists(path):
            os.makedirs(path)
        return path


class ImageGenerator:
    @staticmethod
    def generate_images(path):
        # Генерация всех изображений
        ImageGenerator.generate_bw_image(path)
        ImageGenerator.generate_gray_image(path)
        ImageGenerator.generate_color_image(path)

    @staticmethod
    def generate_bw_image(path, size=(800, 600)):
        img = Image.new('1', size, 0)
        pixels = np.array(img)
        for y in range(size[1]):
            for x in range(size[0]):
                pixels[y, x] = (x + y) % 100 < 50
        img = Image.fromarray(pixels)
        img.save(os.path.join(path, 'bw_image.png'))

    @staticmethod
    def generate_gray_image(path, size=(800, 600)):
        img = Image.new('L', size, 128)
        pixels = np.array(img)
        for y in range(size[1]):
            for x in range(size[0]):
                pixels[y, x] = (x + y) % 256
        img = Image.fromarray(pixels)
        img.save(os.path.join(path, 'gray_image.png'))

    @staticmethod
    def generate_color_image(path, size=(800, 600)):
        img = Image.new('RGB', size, (255, 0, 0))
        pixels = np.array(img)
        for y in range(size[1]):
            for x in range(size[0]):
                pixels[y, x] = (x % 256, y % 256, (x + y) % 256)
        img = Image.fromarray(pixels)
        img.save(os.path.join(path, 'color_image.png'))


class TextGenerator:
    @staticmethod
    def generate_realistic_text(path, size_mb=5):
        filename = os.path.join(path, 'realistic_text.txt')
        chunks = []

        # Пример текста с разной структурой
        templates = [
            "В чащах юга жил бы цитрус? Да, но фальшивый экземпляр! ",
            "Съешь же ещё этих мягких французских булок, да выпей чаю. ",
            "Широкая электрификация южных губерний даст мощный толчок подъёму сельского хозяйства. ",
            "Летают ли коровы над радугой? Это философский вопрос. ",
            "Размышления о смысле жизни приводят к неожиданным выводам. "
        ]

        # Рассчитываем необходимое количество данных
        target_size = size_mb * 1024 * 1024
        current_size = 0

        with open(filename, 'w', encoding='utf-8') as f:
            while current_size < target_size:
                # Случайно выбираем шаблон и модифицируем его
                chunk = random.choice(templates)
                chunk = chunk * random.randint(1, 5)

                # Добавляем случайные числа
                chunk += ''.join(str(random.randint(0, 9)) * random.randint(0, 5))

                # Добавляем случайные знаки препинания
                chunk += random.choice(['!', '?', '.', ',']) * random.randint(0, 3)

                # Добавляем переносы строк
                chunk += '\n' * random.randint(0, 3)

                # Записываем и считаем размер
                f.write(chunk)
                current_size += len(chunk.encode('utf-8'))

        return filename


class RawConverter:
    @staticmethod
    def convert_all_images(path):
        # Конвертация всех изображений в RAW
        RawConverter.convert_to_raw(
            os.path.join(path, 'bw_image.png'),
            os.path.join(path, 'bw_image.raw'),
            'bw'
        )
        RawConverter.convert_to_raw(
            os.path.join(path, 'gray_image.png'),
            os.path.join(path, 'gray_image.raw'),
            'gray'
        )
        RawConverter.convert_to_raw(
            os.path.join(path, 'color_image.png'),
            os.path.join(path, 'color_image.raw'),
            'color'
        )

    @staticmethod
    def convert_to_raw(image_path, output_path, image_type):
        img = Image.open(image_path)
        if image_type == 'bw':
            img = img.convert('1')
        elif image_type == 'gray':
            img = img.convert('L')
        elif image_type == 'color':
            img = img.convert('RGB')

        pixels = np.array(img)
        with open(output_path, 'wb') as f:
            f.write(b'BW' if image_type == 'bw' else b'GR' if image_type == 'gray' else b'CL')
            f.write(pixels.tobytes())