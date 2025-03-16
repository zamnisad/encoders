# Encoders and Decoders

## Описание

Этот репозиторий содержит реализацию различных алгоритмов сжатия данных, включая RLE, Huffman, LZSS, LZW и другие. Также представлены инструменты для анализа эффективности сжатия.

## Структура проекта

```
├── LICENSE
├── README.md
├── compression_test_data
│   ├── bw_image.png
│   ├── bw_image.raw
│   ├── color_image.png
│   ├── color_image.raw
│   ├── enwik7
│   ├── gray_image.png
│   ├── gray_image.raw
│   ├── real_jpg.jpg
│   ├── real_text.txt
│   └── realistic_text.txt
├── encoders_decoders
│   ├── __init__.py
│   ├── blockProcessor.py
│   ├── bwt.py
│   ├── huffman.py
│   ├── lzss.py
│   ├── lzw.py
│   ├── mtf.py
│   └── rle.py
├── graphs_and_analysis
│   ├── comp_ration.py
│   ├── compression_ratio_vs_buffer_size.png
│   ├── entropy_vs_block_size.png
│   └── graph_entropy.py
├── main.py
├── requirements.txt
└── supplement
    ├── generate.py
    ├── process.py
    └── tests.py
```

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/zamnisad/encoders.git
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
from encoders_decoders import Huffman

path = './path-to-your-file'
with open(path, 'rb') as f:
  data = f.read()
coded = Huffman().encode(data)
decoded = Huffman().decode(coded)

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