# Russian Markets Lab

[![CI](https://github.com/sergey-lastochkin/russian-markets-lab/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/sergey-lastochkin/russian-markets-lab/actions/workflows/ci.yml)

Собираю открытые данные Мосбиржи (MOEX ISS) в аккуратные наборы и смотрю на них в дашборде: ликвидность, фьючерсный базис, исторический риск. Это не торговый робот и не сигналы, это лаборатория.

![Панель по историческим данным MOEX](assets/readme_dashboard_overview.png)

С MOEX ISS данные приходят с задержками, дырами и в неудобном виде. Поэтому у каждого Parquet-файла рядом лежит, откуда он, когда собран, сколько строк и какие у него ограничения. Если данные устарели или биржа не ответила, дашборд так и показывает, а не рисует нули как будто это факт.

Посмотреть дашборд можно без запросов к бирже, на сохранённом наборе:

```bash
git clone https://github.com/sergey-lastochkin/russian-markets-lab.git
cd russian-markets-lab
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
python -m russian_markets_lab.cli dataset-status
streamlit run src/russian_markets_lab/dashboard/app.py
```

А обновить с биржи так:

```bash
python -m russian_markets_lab.cli build-all --tickers-limit 30 --lookback-days 365
```

В репозитории лежит набор от `2026-06-19`, 6 таблиц и 260 строк: инструменты, радар ликвидности, базис фьючерсов, опционная доска, сравнение исполнения. Метаданные к каждому - в [data/processed](data/processed/).

![Радар ликвидности](assets/readme_liquidity_radar.png)

Откуда данные - в [источниках](docs/data_sources.md), как считал - в [методике](docs/methodology.md), как проверял целостность - в [аудите](docs/data_integrity_audit.md).

Пара оговорок. Набор от 19 июня 2026 - это не сегодняшний рынок, перед выводами смотрите время сборки и флаг `is_demo`. В открытых данных нет полного стакана, маршрута брокера и реального исполнения. Риск и стоимость исполнения - оценки по истории с допущениями, а не прогноз. CI проверяет код на сохранённых данных и не ходит на биржу.

Сергей Ласточкин · [t.me/metaanswer](https://t.me/metaanswer) · [другие проекты](https://github.com/sergey-lastochkin)
