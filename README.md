# Encoders and Decoders

## Описание
Этот репозиторий содержит реализацию различных алгоритмов сжатия данных, включая RLE, Huffman, LZSS, LZW и другие. Также представлены инструменты для анализа эффективности сжатия.

## Структура проекта

```
├── README.md                  # Этот файл
├── compression_test_data       # Тестовые данные для сжатия
│   ├── bw_image.png            # Чёрно-белое изображение (PNG)
│   ├── bw_image.raw            # Чёрно-белое изображение (RAW)
│   ├── color_image.png         # Цветное изображение (PNG)
│   ├── color_image.raw         # Цветное изображение (RAW)
│   ├── enwik7                  # Файл с текстовыми данными (Wikipedia dump)
│   ├── gray_image.png          # Градации серого (PNG)
│   ├── gray_image.raw          # Градации серого (RAW)
│   ├── real_jpg.jpg            # Реальное изображение (JPEG)
│   ├── real_text.txt           # Обычный текстовый файл
│   └── realistic_text.txt       # Реалистичный текст для тестирования
├── encoders_decoders           # Реализация алгоритмов сжатия и декомпрессии
│   ├── __init__.py
│   ├── blockProcessor.py       # Обработка блоков данных
│   ├── bwt.py                  # Трансформация Барроуза-Уилера (BWT)
│   ├── huffman.py              # Кодирование Хаффмана
│   ├── lzss.py                 # Алгоритм LZSS
│   ├── lzw.py                  # Алгоритм LZW
│   ├── mtf.py                  # Move-To-Front (MTF)
│   └── rle.py                  # Кодирование длин серий (RLE)
├── generate                    # Генератор тестовых данных
│   └── generate.py             # Скрипт для генерации тестовых файлов
├── graphs_and_analysis         # Графики и анализ
│   ├── comp_ration.py          # Анализ коэффициента сжатия
│   ├── compression_ratio_vs_buffer_size.png  # График: коэффициент сжатия vs размер буфера
│   ├── entropy_vs_block_size.png             # График: энтропия vs размер блока
│   └── graph_entropy.py        # Скрипт для построения графиков энтропии
├── main.py                     # Главный файл проекта
├── requirements.txt            # Зависимости проекта
└── tests.py                    # Тестирование алгоритмов
```

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ZamniProg/encoders.git
   cd encoders
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Использование

Для запуска основного скрипта выполните:
```bash
python main.py
```

Для тестирования алгоритмов:
```bash
python tests.py
```

### Пример использования

```python
from encoders_decoders import huffman

text = "example text"
coded, tree = huffman.encode(text)
decoded = huffman.decode(coded, tree)

print("Encoded:", coded)
print("Decoded:", decoded)
```

## Алгоритмы

Проект включает в себя следующие алгоритмы сжатия:
- **Run-Length Encoding (RLE)** — кодирование длин серий ([Wiki](https://en.wikipedia.org/wiki/Run-length_encoding))
- **Move-To-Front (MTF)** — перестановка частых символов в начало ([Wiki](https://en.wikipedia.org/wiki/Move-to-front_transform))
- **Burrows-Wheeler Transform (BWT)** — перестановка символов для улучшения сжатия ([Wiki](https://en.wikipedia.org/wiki/Burrows%E2%80%93Wheeler_transform))
- **Huffman Coding** — префиксное кодирование на основе частоты символов ([Wiki](https://en.wikipedia.org/wiki/Huffman_coding))
- **LZSS** — алгоритм сжатия, использующий скользящее окно ([Wiki](https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Storer%E2%80%93Szymanski))
- **LZW** — вариация алгоритма LZ78 ([Wiki](https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Welch))

## Визуализация и анализ

В проекте присутствуют скрипты для анализа данных:
- `comp_ration.py` — анализ коэффициента сжатия
- `graph_entropy.py` — анализ энтропии текста и её зависимости от размера блока

## Лицензия
Этот проект распространяется под лицензией MIT. См. [LICENSE](LICENSE) для деталей.
