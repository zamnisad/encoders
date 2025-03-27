import pandas as pd
from supplement.process import *


def checkout():
    files = ['bw_image.raw',
             'color_image.raw',
             'gray_image.raw',
             'real_text.txt',
             'enwik7',
             'test.exe',
             'real_jpg.jpg']
    for name in files:
        path = Path(os.path.join("./compression_test_data/", name))
        if not path.exists():
            print(f"Файл {name} не найден!")
            continue

        manager = CompressionManager()
        with open(path, 'rb') as f:
            data = f.read()
        manager.benchmark(data)
        manager.print_benchmark_results()

        manager.run_all_algorithms(path)

        df = pd.DataFrame.from_dict(
            manager.results,
            orient='index',
            columns=[
                "Исходный размер (байты)",
                "Сжатый размер (байты)",
                "Коэффициент сжатия",
                "Время кодирования (сек)",
                "Время декодирования (сек)",
                "Общее время (сек)"
            ]
        )

        df = df.round({
            "Коэффициент сжатия": 3,
            "Время кодирования (сек)": 4,
            "Время декодирования (сек)": 4,
            "Общее время (сек)": 4
        })

        df["Исходный размер (байты)"] = df["Исходный размер (байты)"].astype(int)
        df["Сжатый размер (байты)"] = df["Сжатый размер (байты)"].astype(int)

        os.makedirs('./results', exist_ok=True)
        df.to_csv(
            f'./results/results_{name}.csv',
            index=True,
            index_label='Алгоритм',
            encoding='utf-8-sig',
            sep=';',
            float_format='%.3f'
        )

        print(f"Результаты для {name} сохранены в ./results/results_{name}.csv")


if __name__ == "__main__":
    checkout()