# Источники данных

## MOEX ISS

Russian Markets Lab использует публичные и задержанные данные MOEX ISS.

Основные группы endpoint:

- акции TQBR: инструменты и рыночные данные;
- дневные свечи TQBR;
- фьючерсы FORTS: инструменты и рыночные данные;
- опционы FORTS: инструменты и рыночные данные.

Закрытых API, учётных данных брокера и платных потоков реального времени нет.

## Как устроена загрузка

Сейчас реализован только MOEX ISS. Обработанные наборы хранятся в таблицах pandas/Parquet, а аналитика работает с DataFrame, а не с прямыми ответами API. Другие источники можно добавить позднее, если привести их к ожидаемой схеме; это направление развития, не готовая универсальная абстракция.

## Исходный кэш

Исходные таблицы хранятся по пути:

`data/raw/<dataset_name>/<YYYYMMDD_HHMMSS>.parquet`

У каждого файла есть `*.metadata.json` с источником, endpoint, параметрами, временем, числом строк, колонками и ограничениями.

## Обработанные наборы

В `data/processed/` лежат Parquet-файлы с метаданными:

- `market_universe.parquet`;
- `liquidity_radar.parquet`;
- `futures_basis.parquet`;
- `options_chain_features.parquet`;
- `risk_snapshot.parquet`;
- `execution_comparison.parquet`.

Построить наборы можно командой `python -m russian_markets_lab.cli build-all`, а проверить происхождение – `python -m russian_markets_lab.cli dataset-status`.
