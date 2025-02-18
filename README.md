# Лабораторная работа №1 
Работу выполнил Мяков Тимофей ИАД24

## Набор данных
Используется набор данных [google/jigsaw_toxicity_pred](https://huggingface.co/datasets/google/jigsaw_toxicity_pred) <br>
Для более разнообразной визуализации были сгенерированы колонки в датасете **device** и **age**.

## ML задача
Для ML части используется pretrain модель [s-nlp/roberta_toxicity_classifier](https://huggingface.co/s-nlp/roberta_toxicity_classifier)

## Структура проекта
```bash
.
├── venv/                     # Виртуальное окружение Python
├── data/                     # Исходные и обработанные данные
│   ├── train_augmented.csv   # Аугментированные данные
│   └── train.csv            # Оригинальные данные
├── img/                      # Визуализации и графики
│   ├── metrics.jpeg          # Метрики модели
│   ├── model_infer_analysis.jpeg  # Анализ предсказаний
│   └── raw_data_analysis.jpeg     # EDA исходных данных
├── src/                      # Исходный код
│   ├── analysis.py           # Анализ данных
│   ├── config.yaml           # Настройки проекта
│   ├── extraction.py         # Загрузка данных
│   └── processing.py         # Препроцессинг
├── .gitignore                # Игнорируемые файлы
├── app.py                    # Главное приложение
├── docker-compose.yaml       # Конфигурация Docker
├── pipe.ipynb                # Пайплайн в Jupyter
├── README.md                 # Документация
└── start.sh                  # Скрипт запуска
```

## Визуализация
Визуализация выполнена на streamlit:
- Анализ сырых данных <figure><img src="img/raw_data_analysis.jpeg" alt="drawing" width="500"/></figure>

- Анализ инференса модели <figure><img src="img/model_infer_analysis.jpeg" alt="drawing" width="500"/></figure>

- Метрики качества модели <figure><img src="img/metrics.jpeg" alt="drawing" width="500"/></figure>

## Запуск
- Скачайте docker образ kafka: `docker pull bitnami/kafka` и образ zookeeper: `docker pull bitnami/zookeeper`
- `pip install -r requirements.txt`
- `docker-compose up -d`
- Запуск скриптов в приведенном порядке в разных терминалах:
```
python src/extraction.py 
python src/processing.py
python src/analysis.py
streamlit run app/app.py
```
