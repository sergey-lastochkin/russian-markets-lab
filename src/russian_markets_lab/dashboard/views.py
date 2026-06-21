"""Streamlit dashboard view renderers."""

from __future__ import annotations

import builtins
from html import escape

import pandas as pd
import streamlit as st

from russian_markets_lab.analytics.execution import explain_execution_assumptions
from russian_markets_lab.dashboard.charts import (
    execution_cost_bar,
    futures_basis_bar,
    liquidity_score_bar,
    market_liquidity_bar,
    market_volatility_scatter,
    options_smile_chart,
    options_surface_heatmap,
    turnover_bar,
)
from russian_markets_lab.dashboard.components import (
    hero,
    metric_cards,
    note,
    section_header,
    show_dataset_metadata,
    show_demo_warning,
    show_limitations_note,
    show_methodology_link,
    show_missing_data_message,
    status_rows,
    terminal_title,
)
from russian_markets_lab.dashboard.data_loader import (
    load_metadata,
    load_processed_dataset,
)
from russian_markets_lab.demo.demo_data import load_demo_equity_curve

DATASETS = [
    "market_universe",
    "liquidity_radar",
    "futures_basis",
    "options_chain_features",
    "risk_snapshot",
    "execution_comparison",
]

TAB_LABELS_EN = [
    "Market Map",
    "Liquidity Radar",
    "Futures Basis",
    "Options Surface",
    "Risk Engine",
    "Execution Simulator",
    "Strategy Research Lab",
]

TAB_LABELS_RU = [
    "Карта рынка",
    "Ликвидность",
    "Фьючерсный базис",
    "Опционы",
    "Риск",
    "Исполнение",
    "Стратегии",
]

COLUMN_LABELS_EN = {
    "ticker": "Ticker",
    "name": "Name",
    "board": "Board",
    "avg_daily_value": "ADV, RUB",
    "median_daily_value": "Median value, RUB",
    "realized_volatility": "Realized vol",
    "tradable_flag": "Tradable",
    "tradability_score": "Tradability",
    "data_quality_score": "Data quality",
    "liquidity_score": "Liquidity score",
    "liquidity_regime": "Liquidity regime",
    "spread_source": "Spread source",
    "avg_value_component": "Value component",
    "volume_component": "Volume component",
    "trade_count_component": "Trade component",
    "spread_component": "Spread component",
    "volatility_penalty": "Volatility penalty",
    "data_quality_component": "Data quality component",
    "quoted_spread_bps": "Quoted spread, bps",
    "spread_bps": "Spread, bps",
    "num_trades": "Trades",
    "turnover": "Turnover",
    "underlying": "Underlying",
    "spot_secid": "Spot",
    "futures_secid": "Future",
    "spot_price": "Spot px",
    "futures_price": "Futures px",
    "expiry": "Expiry",
    "days_to_expiry": "Days to expiry",
    "basis_pct": "Basis",
    "annualized_basis": "Ann. basis",
    "volume": "Volume",
    "open_interest": "Open interest",
    "liquidity_filter": "Liquidity filter",
    "signal": "Signal",
    "confidence": "Confidence",
    "secid": "SECID",
    "shortname": "Short name",
    "option_type": "Type",
    "strike": "Strike",
    "expiration": "Expiration",
    "market_price": "Market px",
    "spot": "Spot",
    "moneyness": "Moneyness",
    "time_to_expiry": "TTE, years",
    "implied_volatility": "IV",
    "delta": "Delta",
    "gamma": "Gamma",
    "vega": "Vega",
    "theta": "Theta",
    "section": "Section",
    "metric": "Metric",
    "value": "Value",
    "method": "Method",
    "window": "Window",
    "limitations": "Limitations",
    "instrument": "Instrument",
    "weight": "Weight",
    "annualized_volatility": "Ann. volatility",
    "risk_contribution_pct": "Risk contribution",
    "risk_contribution_vol": "Risk contribution vol",
    "execution_style": "Style",
    "avg_slippage_bps": "Slippage, bps",
    "commission_bps": "Commission, bps",
    "market_impact_bps": "Impact, bps",
    "total_cost_bps": "Total cost, bps",
    "fill_rate": "Fill rate",
    "execution_risk": "Execution risk",
    "total_cost_rub": "Total cost, RUB",
    "module": "Module",
    "research use": "Research use",
    "failure mode": "Failure mode",
    "research implication": "Research implication",
}

COLUMN_LABELS_RU = {
    "ticker": "Тикер",
    "name": "Название",
    "board": "Режим",
    "avg_daily_value": "Оборот, RUB",
    "median_daily_value": "Медиана оборота, RUB",
    "realized_volatility": "Реализ. вол.",
    "tradable_flag": "Торгуемый",
    "tradability_score": "Скор",
    "data_quality_score": "Качество данных",
    "liquidity_score": "Скор ликвидности",
    "liquidity_regime": "Режим ликвидности",
    "spread_source": "Источник спреда",
    "avg_value_component": "Компонент оборота",
    "volume_component": "Компонент объёма",
    "trade_count_component": "Компонент сделок",
    "spread_component": "Компонент спреда",
    "volatility_penalty": "Штраф волатильности",
    "data_quality_component": "Компонент качества",
    "quoted_spread_bps": "Котир. спред, б.п.",
    "spread_bps": "Спред, б.п.",
    "num_trades": "Сделки",
    "turnover": "Оборот",
    "underlying": "База",
    "spot_secid": "Спот",
    "futures_secid": "Фьючерс",
    "spot_price": "Спот px",
    "futures_price": "Фьючерс px",
    "expiry": "Экспирация",
    "days_to_expiry": "Дней до эксп.",
    "basis_pct": "Базис",
    "annualized_basis": "Год. базис",
    "volume": "Объём",
    "open_interest": "Открытый интерес",
    "liquidity_filter": "Фильтр ликв.",
    "signal": "Оценка",
    "confidence": "Надёжность",
    "secid": "Код",
    "shortname": "Короткое имя",
    "option_type": "Тип",
    "strike": "Страйк",
    "expiration": "Экспирация",
    "market_price": "Цена опциона",
    "spot": "Спот",
    "moneyness": "Денежность",
    "time_to_expiry": "Срок, лет",
    "implied_volatility": "Подраз. вол.",
    "delta": "Дельта",
    "gamma": "Гамма",
    "vega": "Вега",
    "theta": "Тета",
    "section": "Раздел",
    "metric": "Метрика",
    "value": "Значение",
    "method": "Метод",
    "window": "Окно",
    "limitations": "Ограничения",
    "instrument": "Инструмент",
    "weight": "Вес",
    "annualized_volatility": "Год. волатильность",
    "risk_contribution_pct": "Вклад в риск",
    "risk_contribution_vol": "Вклад в вол.",
    "execution_style": "Способ",
    "avg_slippage_bps": "Проскальз., б.п.",
    "commission_bps": "Комиссия, б.п.",
    "market_impact_bps": "Воздействие, б.п.",
    "total_cost_bps": "Итого, б.п.",
    "fill_rate": "Доля исп.",
    "execution_risk": "Риск исполнения",
    "total_cost_rub": "Итого, RUB",
    "module": "Модуль",
    "research use": "Назначение",
    "failure mode": "Почему может не сработать",
    "research implication": "Вывод для исследования",
    "assumption": "Допущение",
    "description": "Описание",
}

COMPACT_VALUE_COLUMNS = {
    "avg_daily_value",
    "median_daily_value",
    "value",
    "total_cost_rub",
}
PERCENT_COLUMNS = {
    "realized_volatility",
    "basis_pct",
    "annualized_basis",
    "implied_volatility",
    "fill_rate",
    "annualized_volatility",
    "risk_contribution_pct",
}
BPS_COLUMNS = {
    "spread_bps",
    "avg_slippage_bps",
    "commission_bps",
    "market_impact_bps",
    "total_cost_bps",
}
SCORE_COLUMNS = {
    "tradability_score",
    "data_quality_score",
    "liquidity_score",
    "avg_value_component",
    "volume_component",
    "trade_count_component",
    "spread_component",
    "volatility_penalty",
    "data_quality_component",
    "moneyness",
}
PRICE_COLUMNS = {
    "spot_price",
    "futures_price",
    "market_price",
    "spot",
    "strike",
}
INTEGER_COLUMNS = {
    "num_trades",
    "days_to_expiry",
    "volume",
    "open_interest",
}
GREEK_COLUMNS = {
    "delta",
    "gamma",
    "vega",
    "theta",
    "time_to_expiry",
}
CATEGORICAL_COLUMNS = {
    "option_type",
    "signal",
    "confidence",
    "liquidity_regime",
    "spread_source",
    "execution_style",
    "execution_risk",
    "section",
    "metric",
}


def tab_labels(lang: str) -> list[str]:
    """Return dashboard tab labels for the selected UI language."""

    return TAB_LABELS_RU if lang == "ru" else TAB_LABELS_EN


def ui(lang: str, en: str, ru: str) -> str:
    """Return localized dashboard copy."""

    return ru if lang == "ru" else en


def numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    """Return a numeric Series for presentation calculations."""

    if column not in df.columns:
        return pd.Series(dtype="float64")
    return pd.to_numeric(df[column], errors="coerce")


def lookup_metric_value(metric_lookup: dict[object, object], *names: str) -> object:
    """Return a metric value by trying exact and normalized metric names."""

    normalized_lookup = {
        str(key).strip().lower().replace("_", " "): value
        for key, value in metric_lookup.items()
    }
    for name in names:
        if name in metric_lookup:
            return metric_lookup[name]
        normalized = name.strip().lower().replace("_", " ")
        if normalized in normalized_lookup:
            return normalized_lookup[normalized]
    return None


def format_number(value: object, decimals: int = 2, lang: str = "en") -> str:
    """Format numbers for compact terminal cards."""

    if value is None or pd.isna(value):
        return "n/a"
    number = float(value)
    if abs(number) >= 1_000_000_000:
        suffix = " млрд" if lang == "ru" else "B"
        return f"{number / 1_000_000_000:.{decimals}f}{suffix}"
    if abs(number) >= 1_000_000:
        suffix = " млн" if lang == "ru" else "M"
        return f"{number / 1_000_000:.{decimals}f}{suffix}"
    if abs(number) >= 1_000:
        suffix = " тыс" if lang == "ru" else "K"
        return f"{number / 1_000:.{decimals}f}{suffix}"
    return f"{number:.{decimals}f}"


def format_percent(value: object, decimals: int = 1) -> str:
    """Format a ratio as a percent for dashboard cards."""

    if value is None or pd.isna(value):
        return "н/д"
    return f"{float(value) * 100:.{decimals}f}%"


def format_compact_value(value: object, lang: str = "en") -> str:
    """Format large monetary or turnover values with compact suffixes."""

    if value is None or pd.isna(value):
        return ""
    number = float(value)
    sign = "-" if number < 0 else ""
    number = abs(number)
    if number >= 1_000_000_000:
        suffix = " млрд" if lang == "ru" else "B"
        return f"{sign}{number / 1_000_000_000:.2f}{suffix}"
    if number >= 1_000_000:
        suffix = " млн" if lang == "ru" else "M"
        return f"{sign}{number / 1_000_000:.2f}{suffix}"
    if number >= 1_000:
        suffix = " тыс" if lang == "ru" else "K"
        return f"{sign}{number / 1_000:.1f}{suffix}"
    return f"{sign}{number:.2f}"


def format_table_value(column: str, value: object, lang: str = "ru") -> object:
    """Format one table cell without changing the underlying dataset."""

    if value is None or pd.isna(value):
        return ""
    normalized = str(value).strip().lower()
    if lang == "ru" and column == "option_type":
        return {"call": "колл", "put": "пут"}.get(normalized, value)
    if lang == "ru" and column == "signal":
        return {
            "cheap": "Дисконт",
            "fair": "Нейтрально",
            "rich": "Премия",
            "unknown": "Нет данных",
        }.get(normalized, value)
    if lang == "ru" and column == "confidence":
        return {
            "high": "высокая",
            "medium": "средняя",
            "low": "низкая",
            "unknown": "неизвестно",
        }.get(normalized, value)
    if lang == "ru" and column == "liquidity_regime":
        return {
            "liquid": "ликвидный",
            "watch": "наблюдение",
            "illiquid": "низкая ликвидность",
            "insufficient_data": "недостаточно данных",
        }.get(normalized, value)
    if lang == "ru" and column == "spread_source":
        return {
            "quoted": "котируемый",
            "reported": "из данных",
            "quoted_or_reported": "котировка/данные",
            "unavailable": "нет данных",
        }.get(normalized, value)
    if lang == "ru" and column == "execution_risk":
        return {
            "low": "низкий",
            "medium": "средний",
            "high": "высокий",
            "low fill risk, higher immediacy cost": "низкий риск неисполнения, выше цена срочности",
            "fill uncertainty": "неопределённость исполнения",
            "schedule risk": "риск расписания",
            "volume profile risk": "риск профиля объёма",
        }.get(normalized, value)
    if lang == "ru" and column == "execution_style":
        return {
            "market": "рыночная заявка",
            "limit": "лимитная заявка",
            "twap": "TWAP",
            "vwap": "VWAP",
        }.get(normalized, value)
    if lang == "ru" and column == "section":
        return {
            "portfolio": "портфель",
            "portfolio_metrics": "портфель",
            "correlation": "корреляция",
            "stress": "стресс",
            "risk_contribution": "вклад в риск",
        }.get(normalized, value)
    if lang == "ru" and column == "metric":
        return {
            "mean_daily_return": "средняя дневная доходность",
            "annualized_volatility": "годовая волатильность",
            "var 95%": "VaR 95%",
            "cvar 95%": "CVaR 95%",
            "max_drawdown": "макс. просадка",
            "observations": "наблюдения",
            "avg_pairwise_correlation": "средняя парная корреляция",
            "asset_count": "число активов",
            "moex index -15%": "индекс MOEX -15%",
            "usd/rub +10%": "USD/RUB +10%",
            "interest rates +300 bps": "ставки +300 б.п.",
            "oil -20%": "нефть -20%",
            "single-name gap down -25%": "гэп отдельной бумаги -25%",
            "volatility x2": "волатильность x2",
        }.get(normalized, value)
    if lang == "ru" and column == "method":
        return {
            "historical arithmetic mean": "историческое среднее",
            "daily standard deviation annualized by sqrt(252)": "дневное стандартное отклонение, годовое через sqrt(252)",
            "historical 5th percentile loss": "исторический 5-й перцентиль убытка",
            "average loss beyond historical var cutoff": "средний убыток хуже VaR",
            "peak-to-trough drawdown on compounded returns": "просадка от пика до минимума на накопленной доходности",
            "valid daily return count": "число валидных дневных доходностей",
            "average off-diagonal correlation": "средняя внедиагональная корреляция",
            "number of return columns": "число рядов доходности",
            "simplified scenario shock": "упрощённый сценарный шок",
        }.get(normalized, value)
    if lang == "ru" and column == "limitations":
        return {
            "backward-looking daily sample.": "Историческая дневная выборка.",
            "assumes daily volatility scales with square-root time.": "Предполагается масштабирование волатильности через корень времени.",
            "does not model shocks absent from the sample.": "Не моделирует шоки, которых не было в выборке.",
            "tail estimate can be unstable in short samples.": "Оценка хвоста нестабильна на коротких выборках.",
            "depends on the selected historical window.": "Зависит от выбранного исторического окна.",
            "older observations may reflect stale regimes.": "Старые наблюдения могут относиться к устаревшим режимам.",
            "correlation is historical and unstable across regimes.": "Корреляция историческая и нестабильна между режимами.",
            "asset set depends on available candles.": "Набор активов зависит от доступных свечей.",
            "no margin, liquidation, funding or order book impact model.": "Нет модели маржи, ликвидации, фондирования и влияния стакана.",
        }.get(normalized, value)
    if lang == "ru" and column == "window":
        if normalized == "current equal-weight portfolio":
            return "текущий равновзвешенный портфель"
        if normalized.endswith(" observations"):
            return normalized.replace(" observations", " наблюдений")
    if isinstance(value, bool):
        if lang == "ru":
            return "Да" if value else "Нет"
        return "Yes" if value else "No"
    if column in COMPACT_VALUE_COLUMNS:
        return format_compact_value(value, lang)
    if column in PERCENT_COLUMNS:
        return f"{float(value) * 100:.2f}%"
    if column in BPS_COLUMNS:
        return f"{float(value):.1f}"
    if column in SCORE_COLUMNS:
        return f"{float(value):.2f}"
    if column in PRICE_COLUMNS:
        return f"{float(value):.2f}"
    if column in INTEGER_COLUMNS:
        return f"{float(value):,.0f}"
    if column in GREEK_COLUMNS:
        return f"{float(value):.4f}"
    return value


def safe_html(value: object) -> str:
    """Convert dashboard table values to escaped HTML text."""

    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return escape(", ".join(builtins.str(item) for item in value))
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return escape(builtins.str(value))


def prepare_table_display(
    df: pd.DataFrame, columns: list[str] | None = None, lang: str = "ru"
) -> pd.DataFrame:
    """Return a display-only table with compact labels and formatted values."""

    display = df.copy()
    if columns:
        display = display[[col for col in columns if col in display.columns]]
    for column in display.columns:
        if (
            column in COMPACT_VALUE_COLUMNS
            or column in PERCENT_COLUMNS
            or column in BPS_COLUMNS
            or column in SCORE_COLUMNS
            or column in PRICE_COLUMNS
            or column in INTEGER_COLUMNS
            or column in GREEK_COLUMNS
            or column in CATEGORICAL_COLUMNS
            or pd.api.types.is_bool_dtype(display[column])
        ):
            display[column] = display[column].map(
                lambda value, current=column: format_table_value(current, value, lang)
            )
    labels = COLUMN_LABELS_RU if lang == "ru" else COLUMN_LABELS_EN
    return display.rename(columns={col: labels.get(col, col) for col in display})


def latest_generated_at(statuses: pd.DataFrame, lang: str = "ru") -> str:
    """Return latest generated_at value for display."""

    if statuses.empty or "generated_at" not in statuses.columns:
        return "н/д" if lang == "ru" else "n/a"
    values = statuses["generated_at"].dropna().astype(str)
    if values.empty:
        return "н/д" if lang == "ru" else "n/a"
    parsed = pd.to_datetime(values.max(), errors="coerce", utc=True)
    if pd.isna(parsed):
        return values.max()
    msk = parsed.tz_convert("Europe/Moscow")
    if lang == "ru":
        return msk.strftime("%d.%m.%Y\n%H:%M (МСК)")
    return msk.strftime("%Y-%m-%d\n%H:%M (MSK)")


def render_sidebar(demo_mode: bool, statuses: pd.DataFrame, lang: str = "ru") -> None:
    """Render the sidebar research terminal controls."""

    terminal_title("Russian Markets Lab", st.sidebar)
    st.sidebar.caption(
        ui(
            lang,
            "MOEX liquidity, derivatives, risk and execution research.",
            "Исследование ликвидности, деривативов, риска и исполнения на MOEX.",
        )
    )

    status_modes = set(statuses.get("data_mode", pd.Series(dtype=object)).dropna())
    has_stale = bool(statuses.get("stale", pd.Series(dtype=bool)).any())
    if demo_mode:
        mode = ui(lang, "Demo", "Демо")
        mode_status = "warn"
    elif "missing" in status_modes:
        mode = ui(lang, "Partial cache", "Частичный кэш")
        mode_status = "warn"
    elif has_stale:
        mode = ui(lang, "Stale cache", "Устаревший кэш")
        mode_status = "warn"
    else:
        mode = ui(lang, "Processed cache", "Обработанный кэш")
        mode_status = "good"
    readable = bool(statuses.get("parquet_readable", pd.Series(dtype=bool)).all())
    status_rows(
        [
            (ui(lang, "Data mode", "Режим данных"), mode, mode_status),
            (
                ui(lang, "Parquet", "Файлы данных"),
                (
                    ui(lang, "ready", "готово")
                    if readable
                    else ui(lang, "check", "проверить")
                ),
                "good" if readable else "warn",
            ),
        ],
        st.sidebar,
    )
    if demo_mode:
        st.sidebar.warning(
            ui(
                lang,
                "Demo mode is enabled. Displayed values may be illustrative and are not real market research output.",
                "Демо-режим включён. Показанные значения могут быть иллюстративными и не являются реальным исследовательским выводом.",
            )
        )

    available = int(statuses["exists"].sum()) if "exists" in statuses.columns else 0
    total_rows = (
        int(statuses["row_count"].sum()) if "row_count" in statuses.columns else 0
    )
    st.sidebar.caption(
        ui(
            lang,
            f"Datasets: {available}/{len(DATASETS)} | Rows: {total_rows:,}",
            f"Наборы данных: {available}/{len(DATASETS)} | строк: {total_rows:,}",
        )
    )
    st.sidebar.caption(
        ui(
            lang,
            f"Latest update: {latest_generated_at(statuses, lang)}",
            f"Последнее обновление: {latest_generated_at(statuses, lang)}",
        )
    )

    terminal_title(ui(lang, "Dataset Status", "Статус данных"), st.sidebar)
    status_columns = [
        "dataset_name",
        "data_mode",
        "exists",
        "parquet_readable",
        "metadata_exists",
        "row_count",
        "stale",
    ]
    status_display = statuses[
        [col for col in status_columns if col in statuses.columns]
    ]
    if lang == "ru":
        status_display = status_display.rename(
            columns={
                "dataset_name": "Датасет",
                "data_mode": "Режим",
                "exists": "Есть",
                "parquet_readable": "Файл",
                "metadata_exists": "Метаданные",
                "row_count": "Строки",
                "stale": "Старые",
            }
        )
        status_display["Датасет"] = status_display["Датасет"].replace(
            {
                "market_universe": "Инструменты",
                "liquidity_radar": "Ликвидность",
                "futures_basis": "Базис",
                "options_chain_features": "Опционы",
                "risk_snapshot": "Риск",
                "execution_comparison": "Исполнение",
            }
        )
    st.sidebar.dataframe(
        status_display,
        width="stretch",
        hide_index=True,
        height=245,
    )

    terminal_title(ui(lang, "Quick Commands", "Команды"), st.sidebar)
    st.sidebar.code("python -m russian_markets_lab.cli build-all", language="bash")
    st.sidebar.code("python -m russian_markets_lab.cli dataset-status", language="bash")

    terminal_title(ui(lang, "References", "Документы"), st.sidebar)
    st.sidebar.caption("docs/methodology.md")
    st.sidebar.caption("docs/data_sources.md")
    st.sidebar.caption("docs/limitations.md")
    st.sidebar.caption("docs/project_status.md")

    terminal_title(ui(lang, "About", "О проекте"), st.sidebar)
    st.sidebar.caption(
        ui(
            lang,
            "Developer: Sergey Goncharov. Research prototype, not investment advice.",
            "Разработчик: Сергей Гончаров. Исследовательский прототип, не инвестиционная рекомендация.",
        )
    )


def render_top_status_bar(
    demo_mode: bool, statuses: pd.DataFrame, lang: str = "ru"
) -> None:
    """Render compact top-level dataset status metrics."""

    available = int(statuses["exists"].sum()) if "exists" in statuses.columns else 0
    total_rows = (
        int(statuses["row_count"].sum()) if "row_count" in statuses.columns else 0
    )
    readable = bool(statuses.get("parquet_readable", pd.Series(dtype=bool)).all())
    status_modes = set(statuses.get("data_mode", pd.Series(dtype=object)).dropna())
    has_stale = bool(statuses.get("stale", pd.Series(dtype=bool)).any())
    if demo_mode:
        mode_value = ui(lang, "Demo", "Демо")
        mode_help = ui(lang, "explicit opt-in demo", "демо только вручную")
    elif "missing" in status_modes:
        mode_value = ui(lang, "Partial cache", "Частичный кэш")
        mode_help = ui(lang, "missing datasets visible", "пропуски видны")
    elif has_stale:
        mode_value = ui(lang, "Stale cache", "Устаревший кэш")
        mode_help = ui(lang, "rebuild recommended", "лучше пересобрать")
    else:
        mode_value = ui(lang, "Processed cache", "Обработанный кэш")
        mode_help = ui(lang, "MOEX ISS-derived files", "файлы из MOEX ISS")
    metric_cards(
        [
            (
                ui(lang, "Available datasets", "Наборы данных"),
                f"{available}/{len(DATASETS)}",
                ui(lang, "processed parquet", "обработанные файлы"),
            ),
            (
                ui(lang, "Total processed rows", "Всего строк"),
                f"{total_rows:,}",
                ui(lang, "metadata-backed count", "по файлам метаданных"),
            ),
            (
                ui(lang, "Data mode", "Режим данных"),
                mode_value,
                mode_help,
            ),
            (
                ui(lang, "Latest generated_at", "Последнее обновление"),
                latest_generated_at(statuses, lang),
                None,
            ),
            (
                ui(lang, "Parquet readability", "Чтение файлов"),
                (
                    ui(lang, "OK", "Готово")
                    if readable
                    else ui(lang, "Check", "Проверить")
                ),
                ui(lang, "pyarrow required", "требуется pyarrow"),
            ),
        ]
    )


def table(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    height: int = 340,
    lang: str = "ru",
) -> None:
    """Render a compact dataframe table."""

    display = prepare_table_display(df, columns, lang)
    if display.empty:
        note(ui(lang, "No rows to display.", "Нет строк для отображения."))
        return

    header = "".join(f"<th>{safe_html(column)}</th>" for column in display.columns)
    rows = []
    for values in display.itertuples(index=False, name=None):
        cells = "".join(f"<td>{safe_html(value)}</td>" for value in values)
        rows.append(f"<tr>{cells}</tr>")
    st.markdown(
        f'<div class="rml-table-wrap" style="max-height:{height}px;">'
        f'<table class="rml-table"><thead><tr>{header}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def chart(fig, show_modebar: bool = True) -> None:
    """Render Plotly chart with a clean dashboard config."""

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": show_modebar,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            "responsive": True,
        },
    )


def mobile_toggle(label: str, key: str) -> bool:
    """Render a mobile-safe disclosure control."""

    return st.checkbox(label, value=False, key=key)


def execution_assumptions_display(lang: str) -> pd.DataFrame:
    """Return localized execution assumptions for dashboard display."""

    if lang != "ru":
        return explain_execution_assumptions()
    return pd.DataFrame(
        [
            (
                "Переход через спред",
                "Рыночная заявка обычно платит около половины спреда до учёта рыночного воздействия.",
            ),
            (
                "Рыночное воздействие",
                "Воздействие на цену оценивается через долю участия в обороте и волатильность.",
            ),
            (
                "Исполнение лимитной заявки",
                "Доля исполнения лимитной заявки является допущением, а не гарантией.",
            ),
            (
                "TWAP/VWAP",
                "Расписания упрощены и не моделируют очередь заявок внутри дня.",
            ),
        ],
        columns=["assumption", "description"],
    )


def render_mobile_view(
    statuses: pd.DataFrame, demo_mode: bool, lang: str = "ru"
) -> None:
    """Render a compact phone-friendly dashboard view for outreach links."""

    hero(
        "Russian Markets Lab",
        ui(
            lang,
            "Mobile overview of MOEX liquidity, futures basis, risk and execution diagnostics.",
            "Короткий мобильный обзор: ликвидность MOEX, фьючерсный базис, риск и издержки исполнения.",
        ),
        ui(lang, "MOBILE RESEARCH VIEW", "МОБИЛЬНЫЙ ОБЗОР"),
    )
    note(
        ui(
            lang,
            "This is a research dashboard built on public/delayed MOEX ISS data and processed datasets. "
            "It does not provide trading signals or investment advice.",
            "Это исследовательский дашборд на публичных/задержанных данных MOEX ISS и обработанных датасетах. "
            "Он не даёт торговых сигналов и инвестиционных рекомендаций.",
        )
    )
    if demo_mode:
        show_demo_warning(lang)

    available = int(statuses["exists"].sum()) if "exists" in statuses.columns else 0
    total_rows = (
        int(statuses["row_count"].sum()) if "row_count" in statuses.columns else 0
    )
    readable = bool(statuses.get("parquet_readable", pd.Series(dtype=bool)).all())
    metric_cards(
        [
            (
                ui(lang, "Datasets", "Датасеты"),
                f"{available}/{len(DATASETS)}",
                ui(lang, "processed files", "обработанные файлы"),
            ),
            (
                ui(lang, "Rows", "Строки"),
                f"{total_rows:,}",
                ui(lang, "metadata-backed", "по метаданным"),
            ),
            (
                ui(lang, "Updated", "Обновлено"),
                latest_generated_at(statuses, lang),
                None,
            ),
            (
                ui(lang, "Data mode", "Режим данных"),
                ui(lang, "Demo", "Демо") if demo_mode else ui(lang, "Real", "Реальные"),
                ui(lang, "manual demo opt-in", "демо только вручную"),
            ),
            (
                ui(lang, "Files", "Файлы"),
                (
                    ui(lang, "ready", "готово")
                    if readable
                    else ui(lang, "check", "проверить")
                ),
                ui(lang, "parquet", "parquet"),
            ),
        ]
    )

    labels = (
        ["Обзор", "Ликвидность", "Фьючерсы", "Риск", "Исполнение", "Данные"]
        if lang == "ru"
        else ["Overview", "Liquidity", "Futures", "Risk", "Execution", "Data"]
    )
    section = st.pills(
        ui(lang, "Sections", "Разделы"),
        labels,
        default=labels[0],
        key="mobile_section",
    )
    if section is None:
        section = labels[0]

    if section in {"Обзор", "Overview"}:
        render_mobile_overview(lang)
    elif section in {"Ликвидность", "Liquidity"}:
        render_mobile_liquidity(lang)
    elif section in {"Фьючерсы", "Futures"}:
        render_mobile_futures(lang)
    elif section in {"Риск", "Risk"}:
        render_mobile_risk(lang)
    elif section in {"Исполнение", "Execution"}:
        render_mobile_execution(lang)
    else:
        render_mobile_data(statuses, lang)


def render_mobile_overview(lang: str = "ru") -> None:
    """Render compact mobile market overview."""

    universe = load_processed_dataset("market_universe")
    section_header(
        ui(lang, "Overview", "Обзор"),
        ui(
            lang,
            "What the current processed market snapshot contains.",
            "Что есть в текущем обработанном рыночном срезе.",
        ),
    )
    if universe.empty:
        show_missing_data_message("market_universe", lang)
        return

    score_column = (
        "liquidity_score"
        if "liquidity_score" in universe.columns
        else "tradability_score"
    )
    metric_cards(
        [
            (
                ui(lang, "Instruments", "Инструменты"),
                len(universe),
                ui(lang, "selected instruments", "отобранные инструменты"),
            ),
            (
                ui(lang, "Median turnover", "Медианный оборот"),
                format_number(
                    numeric_series(universe, "avg_daily_value").median(), 2, lang
                ),
                ui(lang, "daily", "за день"),
            ),
            (
                ui(lang, "Median score", "Медианный скор"),
                format_number(numeric_series(universe, score_column).median(), 2, lang),
                ui(lang, "relative rank", "относительный ранг"),
            ),
            (
                ui(lang, "Median vol", "Медианная вол."),
                format_percent(
                    numeric_series(universe, "realized_volatility").median(), 1
                ),
                ui(lang, "annualized", "годовая"),
            ),
        ]
    )
    fig = market_volatility_scatter(universe, lang)
    if fig is not None:
        chart(fig, show_modebar=False)
    if mobile_toggle(
        ui(lang, "Show market table", "Показать таблицу рынка"),
        "mobile_market_table",
    ):
        table(
            universe.sort_values(score_column, ascending=False).head(12),
            [
                "ticker",
                "name",
                "avg_daily_value",
                "realized_volatility",
                score_column,
                "data_quality_score",
            ],
            360,
            lang,
        )


def render_mobile_liquidity(lang: str = "ru") -> None:
    """Render compact mobile liquidity view."""

    liquidity = load_processed_dataset("liquidity_radar")
    section_header(
        ui(lang, "Liquidity", "Ликвидность"),
        ui(
            lang,
            "Rank-based liquidity score, spread fields and regimes.",
            "Ранговый скор ликвидности, поля спреда и режимы ликвидности.",
        ),
    )
    if liquidity.empty:
        show_missing_data_message("liquidity_radar", lang)
        return

    regimes = liquidity.get("liquidity_regime", pd.Series(dtype=object)).value_counts()
    metric_cards(
        [
            (
                ui(lang, "Rows", "Строки"),
                len(liquidity),
                ui(lang, "liquidity snapshot", "срез ликвидности"),
            ),
            (
                ui(lang, "Median score", "Медианный скор"),
                format_number(
                    numeric_series(liquidity, "liquidity_score").median(), 2, lang
                ),
                ui(lang, "relative", "относительный"),
            ),
            (
                ui(lang, "Liquid", "Ликвидные"),
                int(regimes.get("liquid", 0)),
                ui(lang, "regime count", "по режиму"),
            ),
            (
                ui(lang, "Watch/illiquid", "Под наблюдением"),
                int(regimes.get("watch", 0)) + int(regimes.get("illiquid", 0)),
                ui(lang, "needs care", "требует внимания"),
            ),
        ]
    )
    fig = liquidity_score_bar(liquidity, lang)
    if fig is not None:
        chart(fig, show_modebar=False)
    note(
        ui(
            lang,
            "Spread is shown as quoted/reported when available. Otherwise it remains explicit as missing or proxy data.",
            "Спред показывается как котируемый/опубликованный, если доступен. Если нет, это явно отмечается как отсутствующее или прокси-поле.",
        )
    )
    if mobile_toggle(
        ui(lang, "Show liquidity table", "Показать таблицу ликвидности"),
        "mobile_liquidity_table",
    ):
        table(
            liquidity.sort_values("liquidity_score", ascending=False).head(15),
            [
                "ticker",
                "avg_daily_value",
                "spread_bps",
                "spread_source",
                "liquidity_score",
                "liquidity_regime",
            ],
            380,
            lang,
        )


def render_mobile_futures(lang: str = "ru") -> None:
    """Render compact mobile futures basis view."""

    basis = load_processed_dataset("futures_basis")
    section_header(
        ui(lang, "Futures Basis", "Фьючерсный базис"),
        ui(
            lang,
            "Basis diagnostic with signal and confidence coverage.",
            "Диагностика базиса с оценкой и уровнем надёжности.",
        ),
    )
    if basis.empty:
        show_missing_data_message("futures_basis", lang)
        return

    counts = (
        basis.get("signal", pd.Series(dtype=object))
        .fillna("unknown")
        .astype(str)
        .str.lower()
        .value_counts()
    )
    confidence = (
        basis.get("confidence", pd.Series(dtype=object))
        .fillna("unknown")
        .value_counts()
    )
    metric_cards(
        [
            (
                ui(lang, "Rich", "Премия"),
                int(counts.get("rich", 0)),
                ui(lang, "count", "кол-во"),
            ),
            (
                ui(lang, "Fair", "Нейтрально"),
                int(counts.get("fair", 0)),
                ui(lang, "count", "кол-во"),
            ),
            (
                ui(lang, "Cheap", "Дисконт"),
                int(counts.get("cheap", 0)),
                ui(lang, "count", "кол-во"),
            ),
            (
                ui(lang, "Unknown", "Нет данных"),
                int(counts.get("unknown", 0)),
                ui(lang, "count", "кол-во"),
            ),
            (
                ui(lang, "High confidence", "Высокая надёжность"),
                int(confidence.get("high", 0)),
                ui(lang, "valid inputs", "валидные входы"),
            ),
        ]
    )
    present = [
        signal
        for signal in ["rich", "fair", "cheap", "unknown"]
        if int(counts.get(signal, 0)) > 0
    ]
    if len(present) == 1:
        only_signal = present[0]
        note(
            ui(
                lang,
                f"Only {only_signal} contracts are present in the current processed snapshot.",
                f"В текущем обработанном срезе есть только контракты класса {format_table_value('signal', only_signal, 'ru')}.",
            )
        )
    st.warning(
        ui(
            lang,
            "Basis screen is not an arbitrage signal.",
            "Экран базиса не является арбитражным сигналом.",
        )
    )
    fig = futures_basis_bar(basis, lang)
    if fig is not None:
        chart(fig, show_modebar=False)
    if mobile_toggle(
        ui(lang, "Show basis table", "Показать таблицу базиса"),
        "mobile_basis_table",
    ):
        table(
            basis.sort_values("annualized_basis", ascending=False),
            [
                "underlying",
                "futures_secid",
                "days_to_expiry",
                "annualized_basis",
                "confidence",
                "signal",
            ],
            380,
            lang,
        )


def render_mobile_risk(lang: str = "ru") -> None:
    """Render compact mobile risk view."""

    risk = load_processed_dataset("risk_snapshot")
    section_header(
        ui(lang, "Risk", "Риск"),
        ui(
            lang,
            "Historical risk metrics and simplified stress diagnostics.",
            "Исторические метрики риска и упрощённые стресс-сценарии.",
        ),
    )
    if risk.empty:
        show_missing_data_message("risk_snapshot", lang)
        return

    metrics = (
        risk[risk["section"].isin(["portfolio", "portfolio_metrics"])]
        if "section" in risk
        else risk
    )
    metric_lookup = (
        metrics.set_index("metric")["value"].to_dict()
        if {"metric", "value"}.issubset(metrics.columns)
        else {}
    )
    metric_cards(
        [
            (
                "VaR 95",
                format_number(
                    lookup_metric_value(metric_lookup, "VaR 95%", "var_95", "var 95"), 4
                ),
                ui(lang, "historical", "исторический"),
            ),
            (
                "CVaR 95",
                format_number(
                    lookup_metric_value(
                        metric_lookup, "CVaR 95%", "cvar_95", "cvar 95"
                    ),
                    4,
                ),
                ui(lang, "historical", "исторический"),
            ),
            (
                ui(lang, "Volatility", "Волатильность"),
                format_number(
                    lookup_metric_value(
                        metric_lookup, "annualized_volatility", "volatility"
                    ),
                    4,
                ),
                ui(lang, "annualized", "годовая"),
            ),
            (
                ui(lang, "Max drawdown", "Макс. просадка"),
                format_number(
                    lookup_metric_value(metric_lookup, "max_drawdown", "max drawdown"),
                    4,
                ),
                ui(lang, "historical", "историческая"),
            ),
        ]
    )
    stress = (
        risk[risk["section"].astype(str).str.startswith("stress")]
        if "section" in risk.columns
        else pd.DataFrame()
    )
    section_header(ui(lang, "Risk summary", "Сводка риска"))
    table(metrics, ["metric", "value", "method"], 320, lang)
    if mobile_toggle(
        ui(lang, "Show stress scenarios", "Показать стресс-сценарии"),
        "mobile_stress_table",
    ):
        if stress.empty:
            note(
                ui(lang, "No stress rows are available.", "Стресс-сценарии недоступны.")
            )
        else:
            table(stress, ["metric", "value", "method", "limitations"], 320, lang)


def render_mobile_execution(lang: str = "ru") -> None:
    """Render compact mobile execution view."""

    execution = load_processed_dataset("execution_comparison")
    section_header(
        ui(lang, "Execution", "Исполнение"),
        ui(
            lang,
            "Spread, slippage and modelled execution cost.",
            "Спред, проскальзывание и модельные издержки исполнения.",
        ),
    )
    if execution.empty:
        show_missing_data_message("execution_comparison", lang)
        return

    cost = numeric_series(execution, "total_cost_bps")
    best_style = (
        execution.sort_values("total_cost_bps").iloc[0]["execution_style"]
        if "total_cost_bps" in execution.columns and not execution.empty
        else "n/a"
    )
    metric_cards(
        [
            (
                ui(lang, "Best style", "Минимальная стоимость"),
                format_table_value("execution_style", best_style, lang),
                ui(lang, "model output", "вывод модели"),
            ),
            (
                ui(lang, "Median cost", "Медианная стоимость"),
                format_number(cost.median(), 2, lang),
                ui(lang, "bps", "б.п."),
            ),
            (
                ui(lang, "Median fill", "Медианное исполнение"),
                format_percent(numeric_series(execution, "fill_rate").median(), 1),
                ui(lang, "assumption", "допущение"),
            ),
        ]
    )
    fig = execution_cost_bar(execution, lang)
    if fig is not None:
        chart(fig, show_modebar=False)
    if mobile_toggle(
        ui(lang, "Show execution table", "Показать таблицу исполнения"),
        "mobile_execution_table",
    ):
        table(
            execution,
            [
                "execution_style",
                "avg_slippage_bps",
                "commission_bps",
                "market_impact_bps",
                "total_cost_bps",
                "fill_rate",
                "execution_risk",
            ],
            340,
            lang,
        )
    if mobile_toggle(
        ui(lang, "Show assumptions", "Показать допущения"),
        "mobile_execution_assumptions",
    ):
        table(execution_assumptions_display(lang), height=260, lang=lang)


def render_mobile_data(statuses: pd.DataFrame, lang: str = "ru") -> None:
    """Render mobile dataset status view."""

    section_header(
        ui(lang, "Data", "Данные"),
        ui(
            lang,
            "Processed datasets, metadata and local rebuild commands.",
            "Обработанные датасеты, метаданные и команды для пересборки.",
        ),
    )
    status_columns = [
        "dataset_name",
        "data_mode",
        "exists",
        "parquet_readable",
        "metadata_exists",
        "row_count",
        "stale",
        "generated_at",
        "source",
        "is_demo",
    ]
    display = statuses[
        [col for col in status_columns if col in statuses.columns]
    ].copy()
    if lang == "ru":
        display = display.rename(
            columns={
                "dataset_name": "Датасет",
                "data_mode": "Режим",
                "exists": "Есть",
                "parquet_readable": "Parquet читается",
                "metadata_exists": "Метаданные",
                "row_count": "Строки",
                "stale": "Устарел",
                "generated_at": "Обновлено",
                "source": "Источник",
                "is_demo": "Демо",
            }
        )
    table(display, height=420, lang=lang)
    st.code("python -m russian_markets_lab.cli build-all", language="bash")
    st.code("python -m russian_markets_lab.cli dataset-status", language="bash")


def render_market_tab(lang: str = "ru") -> None:
    """Render Market Map tab."""

    universe = load_processed_dataset("market_universe")
    metadata = load_metadata("market_universe")
    section_header(
        ui(lang, "Market Map", "Карта рынка"),
        ui(
            lang,
            "Selected instruments, tradability and data quality.",
            "Отобранные инструменты, торгуемость и качество данных.",
        ),
    )
    if universe.empty:
        show_missing_data_message("market_universe", lang)
    else:
        score_column = (
            "liquidity_score"
            if "liquidity_score" in universe.columns
            else "tradability_score"
        )
        median_adv = numeric_series(universe, "avg_daily_value").median()
        metric_cards(
            [
                (
                    ui(lang, "Instruments", "Инструменты"),
                    len(universe),
                    ui(lang, "selected instruments", "отобранные инструменты"),
                ),
                (
                    ui(lang, "Median ADV", "Медианный оборот"),
                    format_number(median_adv, 2, lang),
                    ui(lang, "daily value", "среднедневной оборот"),
                ),
                (
                    ui(lang, "Median liquidity score", "Медианный скор ликвидности"),
                    format_number(numeric_series(universe, score_column).median(), 2),
                    ui(lang, "rank-based score", "ранговая оценка"),
                ),
                (
                    ui(lang, "Median realized vol", "Медианная реализ. вол."),
                    format_percent(
                        numeric_series(universe, "realized_volatility").median(), 1
                    ),
                    ui(lang, "annualized", "годовая"),
                ),
            ]
        )
        section_header(
            ui(lang, "Liquidity Ranking", "Рейтинг ликвидности"),
        )
        ranking_cols = [
            "ticker",
            "name",
            "board",
            "avg_daily_value",
            "realized_volatility",
            "tradability_score",
            "data_quality_score",
        ]
        table(
            universe.sort_values(score_column, ascending=False), ranking_cols, lang=lang
        )
        fig = market_volatility_scatter(universe, lang)
        if fig is not None:
            chart(fig)
        fig = market_liquidity_bar(universe, lang)
        if fig is not None:
            chart(fig)
        note(
            ui(
                lang,
                "Data quality score combines observation count, missing close/value ratios "
                "and finite volatility checks. It is a diagnostic, not a trading filter.",
                "Скор качества данных учитывает число наблюдений, пропуски цены закрытия и оборота "
                "и конечность волатильности. Это диагностика, а не торговый фильтр.",
            )
        )
    show_dataset_metadata(metadata, lang)
    show_methodology_link("market-universe", lang)
    show_limitations_note(
        ui(
            lang,
            "Public ISS data can be delayed, stale or incomplete.",
            "Публичные ISS-данные могут быть задержанными, устаревшими или неполными.",
        ),
        lang,
    )


def render_liquidity_tab(lang: str = "ru") -> None:
    """Render Liquidity Radar tab."""

    liquidity = load_processed_dataset("liquidity_radar")
    metadata = load_metadata("liquidity_radar")
    section_header(
        ui(lang, "Liquidity Radar", "Радар ликвидности"),
        ui(
            lang,
            "Rank-based liquidity diagnostics and components.",
            "Ранговая диагностика ликвидности и её компонентов.",
        ),
    )
    if liquidity.empty:
        show_missing_data_message("liquidity_radar", lang)
    else:
        score = numeric_series(liquidity, "liquidity_score")
        median_adv = numeric_series(liquidity, "avg_daily_value").median()
        metric_cards(
            [
                (
                    ui(lang, "Rows", "Строки"),
                    len(liquidity),
                    ui(lang, "liquidity snapshot", "срез ликвидности"),
                ),
                (
                    ui(lang, "Median score", "Медианный скор"),
                    format_number(score.median(), 2),
                    ui(lang, "rank-based", "ранговый"),
                ),
                (
                    ui(lang, "Median spread bps", "Медианный спред, б.п."),
                    format_number(numeric_series(liquidity, "spread_bps").median(), 2),
                    ui(lang, "if available", "если доступен"),
                ),
                (
                    ui(lang, "Median ADV", "Медианный оборот"),
                    format_number(median_adv, 2, lang),
                    ui(lang, "daily value", "среднедневной оборот"),
                ),
            ]
        )
        cols = [
            "ticker",
            "avg_daily_value",
            "spread_bps",
            "spread_source",
            "num_trades",
            "realized_volatility",
            "liquidity_score",
            "liquidity_regime",
        ]
        left, right = st.columns(2)
        with left:
            section_header(ui(lang, "Top Liquidity", "Топ ликвидности"))
            table(
                liquidity.sort_values("liquidity_score", ascending=False).head(12),
                cols,
                280,
                lang,
            )
        with right:
            section_header(ui(lang, "Bottom Liquidity", "Низкая ликвидность"))
            table(
                liquidity.sort_values("liquidity_score", ascending=True).head(12),
                cols,
                280,
                lang,
            )
        fig = liquidity_score_bar(liquidity, lang)
        if fig is not None:
            chart(fig)
        fig = turnover_bar(liquidity, lang)
        if fig is not None:
            chart(fig)
        component_cols = [
            "ticker",
            "avg_value_component",
            "volume_component",
            "trade_count_component",
            "spread_component",
            "volatility_penalty",
            "data_quality_component",
            "liquidity_score",
            "liquidity_regime",
            "spread_source",
        ]
        section_header(
            ui(lang, "Liquidity Score Components", "Компоненты скора ликвидности")
        )
        table(
            liquidity.sort_values("liquidity_score", ascending=False).head(20),
            component_cols,
            360,
            lang,
        )
        section_header(ui(lang, "Score Methodology", "Методология скора"))
        note(
            ui(
                lang,
                "The liquidity score is a first-pass diagnostic combining ranked "
                "value, volume/trade activity, quoted or reported spread where available, "
                "data quality, and a volatility penalty. Missing spread is shown explicitly "
                "instead of being treated as a real quote.",
                "Скор ликвидности — первичная диагностика: ранги оборота, объёма/"
                "активности сделок, котируемый или опубликованный спред при наличии, "
                "качество данных и штраф за волатильность. Отсутствующий спред "
                "показывается явно и не выдаётся за реальную котировку.",
            )
        )
    show_dataset_metadata(metadata, lang)
    show_methodology_link("liquidity-score", lang)
    show_limitations_note(
        ui(
            lang,
            "Public ISS data may omit full order book depth.",
            "Публичные ISS-данные могут не содержать полной глубины стакана.",
        ),
        lang,
    )


def render_futures_tab(lang: str = "ru") -> None:
    """Render Futures Basis tab."""

    basis = load_processed_dataset("futures_basis")
    metadata = load_metadata("futures_basis")
    section_header(
        ui(lang, "Futures Basis", "Фьючерсный базис"),
        ui(
            lang,
            "Basis deviation and carry screen.",
            "Отклонение базиса и экран carry.",
        ),
    )
    if basis.empty:
        show_missing_data_message("futures_basis", lang)
    else:
        counts = (
            basis.get("signal", pd.Series(dtype=object))
            .fillna("unknown")
            .astype(str)
            .str.lower()
            .value_counts()
        )
        present_signals = [
            signal
            for signal in ["rich", "fair", "cheap", "unknown"]
            if int(counts.get(signal, 0)) > 0
        ]
        confidence_counts = (
            basis.get("confidence", pd.Series(dtype=object))
            .fillna("unknown")
            .value_counts()
        )
        metric_cards(
            [
                (
                    ui(lang, "Contracts", "Контракты"),
                    len(basis),
                    ui(lang, "mapped futures", "сопоставленные фьючерсы"),
                ),
                (
                    ui(lang, "Rich", "Премия"),
                    int(counts.get("rich", 0)),
                    ui(
                        lang,
                        "screen count",
                        "фьючерс выше спота",
                    ),
                ),
                (
                    ui(lang, "Fair", "Нейтрально"),
                    int(counts.get("fair", 0)),
                    ui(lang, "screen count", "близко к справедливому уровню"),
                ),
                (
                    ui(lang, "Cheap", "Дисконт"),
                    int(counts.get("cheap", 0)),
                    ui(lang, "screen count", "фьючерс ниже спота"),
                ),
                (
                    ui(lang, "Unknown", "Нет данных"),
                    int(counts.get("unknown", 0)),
                    ui(lang, "missing classification", "недостаточно данных"),
                ),
            ]
        )
        if len(present_signals) == 1:
            only_signal = present_signals[0]
            note(
                ui(
                    lang,
                    f"Only {only_signal} contracts are present in the current processed snapshot.",
                    f"В текущем обработанном срезе есть только контракты класса {format_table_value('signal', only_signal, 'ru')}.",
                )
            )
        metric_cards(
            [
                (
                    ui(lang, "High confidence", "Высокая надёжность"),
                    int(confidence_counts.get("high", 0)),
                    ui(lang, "valid prices and liquidity", "цены и ликвидность"),
                ),
                (
                    ui(lang, "Medium confidence", "Средняя надёжность"),
                    int(confidence_counts.get("medium", 0)),
                    ui(lang, "partial liquidity fields", "частичная ликвидность"),
                ),
                (
                    ui(lang, "Low confidence", "Низкая надёжность"),
                    int(confidence_counts.get("low", 0)),
                    ui(lang, "weak liquidity fields", "слабые поля ликвидности"),
                ),
                (
                    ui(lang, "Unknown confidence", "Неизвестная надёжность"),
                    int(confidence_counts.get("unknown", 0)),
                    ui(lang, "missing inputs", "нет входных данных"),
                ),
            ]
        )
        st.warning(
            ui(
                lang,
                "Basis screen is not an arbitrage signal.",
                "Экран базиса не является арбитражным сигналом.",
            )
        )
        fig = futures_basis_bar(basis, lang)
        if fig is not None:
            chart(fig)
        table(
            basis.sort_values("annualized_basis", ascending=False),
            [
                "underlying",
                "spot_secid",
                "futures_secid",
                "spot_price",
                "futures_price",
                "expiry",
                "days_to_expiry",
                "basis_pct",
                "annualized_basis",
                "volume",
                "open_interest",
                "liquidity_filter",
                "confidence",
                "signal",
            ],
            420,
            lang,
        )
    show_dataset_metadata(metadata, lang)
    show_methodology_link("futures-basis", lang)
    show_limitations_note(
        ui(
            lang,
            "Futures-to-spot mapping is best effort and contract specs matter.",
            "Сопоставление фьючерсов со спотом сделано приближённо; спецификации контрактов важны.",
        ),
        lang,
    )


def render_options_tab(lang: str = "ru") -> None:
    """Render Options Surface tab."""

    chain = load_processed_dataset("options_chain_features")
    metadata = load_metadata("options_chain_features")
    section_header(
        ui(lang, "Options Surface", "Опционная поверхность"),
        ui(
            lang,
            "Option chain features, implied volatility and Greeks.",
            "Характеристики опционной цепочки, подразумеваемая волатильность и греки.",
        ),
    )
    if chain.empty:
        show_missing_data_message("options_chain_features", lang)
    else:
        iv = numeric_series(chain, "implied_volatility")
        nan_iv = int(iv.isna().sum()) if not iv.empty else 0
        metric_cards(
            [
                (
                    ui(lang, "Contracts", "Контракты"),
                    len(chain),
                    ui(lang, "option features", "характеристики опционов"),
                ),
                (
                    ui(lang, "Valid IV rows", "Строки с расчётом"),
                    int(iv.notna().sum()),
                    ui(lang, "solver outputs", "результат расчёта"),
                ),
                (
                    ui(lang, "NaN IV rows", "Без IV"),
                    nan_iv,
                    ui(lang, "invalid or unsolved inputs", "нет корректного расчёта"),
                ),
                (
                    ui(lang, "Median moneyness", "Медианная денежность"),
                    format_number(numeric_series(chain, "moneyness").median(), 3),
                    None,
                ),
            ]
        )
        fig = options_smile_chart(chain, lang)
        if fig is not None:
            chart(fig)
        fig = options_surface_heatmap(chain, lang)
        if fig is not None:
            chart(fig)
        table(
            chain,
            [
                "secid",
                "shortname",
                "option_type",
                "strike",
                "expiration",
                "underlying",
                "market_price",
                "spot",
                "moneyness",
                "time_to_expiry",
                "implied_volatility",
                "delta",
                "gamma",
                "vega",
                "theta",
            ],
            420,
            lang,
        )
        note(
            ui(
                lang,
                "Implied volatility is NaN when market price, spot, strike, expiry or solver "
                "conditions are invalid. This is expected for sparse or stale option rows.",
                "Подразумеваемая волатильность не рассчитывается, если рыночная цена, спот, страйк, экспирация "
                "или условия расчёта некорректны. Для разреженных или устаревших "
                "опционных строк это ожидаемо.",
            )
        )
    show_dataset_metadata(metadata, lang)
    show_methodology_link("options-surface", lang)
    show_limitations_note(
        ui(
            lang,
            "Black-Scholes assumptions are simplified for local rates and liquidity.",
            "Допущения Black-Scholes упрощены относительно локальных ставок и ликвидности.",
        ),
        lang,
    )


def render_risk_tab(lang: str = "ru") -> None:
    """Render Risk Engine tab."""

    risk = load_processed_dataset("risk_snapshot")
    metadata = load_metadata("risk_snapshot")
    section_header(
        ui(lang, "Risk Engine", "Риск"),
        ui(
            lang,
            "Historical risk metrics and scenario diagnostics.",
            "Исторические метрики риска и сценарная диагностика.",
        ),
    )
    if risk.empty:
        show_missing_data_message("risk_snapshot", lang)
    else:
        metrics = (
            risk[risk["section"].isin(["portfolio", "portfolio_metrics"])]
            if "section" in risk
            else risk
        )
        metric_lookup = (
            metrics.set_index("metric")["value"].to_dict()
            if {"metric", "value"}.issubset(metrics.columns)
            else {}
        )
        var_95 = lookup_metric_value(metric_lookup, "VaR 95%", "var_95", "var 95")
        cvar_95 = lookup_metric_value(metric_lookup, "CVaR 95%", "cvar_95", "cvar 95")
        volatility = lookup_metric_value(
            metric_lookup, "annualized_volatility", "volatility"
        )
        max_dd = lookup_metric_value(metric_lookup, "max_drawdown", "max drawdown")
        metric_cards(
            [
                (
                    "VaR 95",
                    format_number(var_95, 4),
                    ui(lang, "historical", "исторический"),
                ),
                (
                    "CVaR 95",
                    format_number(cvar_95, 4),
                    ui(lang, "historical", "исторический"),
                ),
                (
                    ui(lang, "Volatility", "Волатильность"),
                    format_number(volatility, 4),
                    ui(lang, "annualized", "годовая"),
                ),
                (
                    ui(lang, "Max drawdown", "Макс. просадка"),
                    format_number(max_dd, 4),
                    ui(lang, "equity curve", "кривая капитала"),
                ),
            ]
        )
        stress = (
            risk[risk["section"].astype(str).str.startswith("stress")]
            if "section" in risk.columns
            else pd.DataFrame()
        )
        contributions = (
            risk[risk["section"].astype(str) == "risk_contribution"]
            if "section" in risk.columns
            else pd.DataFrame()
        )
        section_header(ui(lang, "Risk Summary", "Сводка риска"))
        table(
            metrics,
            ["metric", "value", "method", "window", "limitations"],
            320,
            lang,
        )
        section_header(ui(lang, "Stress Scenarios", "Стресс-сценарии"))
        if stress.empty:
            note(
                ui(
                    lang,
                    "No stress scenario rows are available in the current risk snapshot.",
                    "В текущем risk snapshot нет строк стресс-сценариев.",
                )
            )
        else:
            table(
                stress,
                ["metric", "value", "method", "window", "limitations"],
                320,
                lang,
            )
        if not contributions.empty:
            section_header(
                ui(
                    lang,
                    "Approximate Risk Contribution",
                    "Приближённый вклад в риск",
                )
            )
            table(
                contributions,
                [
                    "instrument",
                    "weight",
                    "annualized_volatility",
                    "risk_contribution_pct",
                    "risk_contribution_vol",
                ],
                320,
                lang,
            )
        section_header(ui(lang, "Risk Snapshot", "Срез риска"))
        table(risk, ["section", "metric", "value", "method", "limitations"], 340, lang)
        note(
            ui(
                lang,
                "Drawdown and correlation charts require richer time-series outputs than the "
                "current compact risk snapshot. The table remains the source of truth here.",
                "Графики просадки и корреляции требуют более полного временного ряда, "
                "чем текущий компактный срез риска. Таблица остаётся источником данных.",
            )
        )
    show_dataset_metadata(metadata, lang)
    show_methodology_link("risk-engine", lang)
    show_limitations_note(
        ui(
            lang,
            "Historical risk is backward-looking and scenarios are simplified.",
            "Исторический риск смотрит назад, а сценарии намеренно упрощены.",
        ),
        lang,
    )


def render_execution_tab(lang: str = "ru") -> None:
    """Render Execution Simulator tab."""

    execution = load_processed_dataset("execution_comparison")
    metadata = load_metadata("execution_comparison")
    section_header(
        ui(lang, "Execution Simulator", "Симулятор исполнения"),
        ui(
            lang,
            "Cost model comparison for execution styles.",
            "Сравнение модели издержек для разных стилей исполнения.",
        ),
    )
    if execution.empty:
        show_missing_data_message("execution_comparison", lang)
    else:
        cost = numeric_series(execution, "total_cost_bps")
        best_style = (
            execution.sort_values("total_cost_bps").iloc[0]["execution_style"]
            if "total_cost_bps" in execution.columns and not execution.empty
            else "n/a"
        )
        best_style_display = format_table_value("execution_style", best_style, lang)
        metric_cards(
            [
                (
                    ui(lang, "Styles", "Стили"),
                    len(execution),
                    ui(
                        lang,
                        "market/limit/TWAP/VWAP",
                        "рыночная / лимитная / TWAP / VWAP",
                    ),
                ),
                (
                    ui(lang, "Lowest cost style", "Минимальная стоимость"),
                    best_style_display,
                    ui(lang, "model output", "вывод модели"),
                ),
                (
                    ui(lang, "Median cost bps", "Медианная стоимость, б.п."),
                    format_number(cost.median(), 2),
                    ui(lang, "total cost", "полные издержки"),
                ),
                (
                    ui(lang, "Median fill rate", "Медианное исполнение"),
                    format_percent(numeric_series(execution, "fill_rate").median(), 1),
                    ui(lang, "assumption", "допущение"),
                ),
            ]
        )
        fig = execution_cost_bar(execution, lang)
        if fig is not None:
            chart(fig)
        table(
            execution,
            [
                "execution_style",
                "avg_slippage_bps",
                "commission_bps",
                "market_impact_bps",
                "total_cost_bps",
                "fill_rate",
                "execution_risk",
                "total_cost_rub",
            ],
            300,
            lang,
        )
        section_header(ui(lang, "Assumptions", "Допущения"))
        table(execution_assumptions_display(lang), height=260, lang=lang)
    show_dataset_metadata(metadata, lang)
    show_methodology_link("execution-simulator", lang)
    show_limitations_note(
        ui(
            lang,
            "No order routing, queue position or real order placement is modeled.",
            "Маршрутизация заявок, очередь и реальное выставление заявок не моделируются.",
        ),
        lang,
    )


def render_strategy_tab(demo_mode: bool, lang: str = "ru") -> None:
    """Render strategy research lab tab."""

    section_header(
        ui(lang, "Strategy Research Lab", "Лаборатория стратегий"),
        ui(
            lang,
            "Templates for systematic research, not predictions.",
            "Шаблоны для систематического исследования, не прогнозы и не обещания доходности.",
        ),
    )
    modules = pd.DataFrame(
        (
            [
                ("Моментум", "Доходность за период, фильтр тренда и волатильности"),
                (
                    "Возврат к среднему",
                    "Z-score, скользящее среднее и пороги входа/выхода",
                ),
                (
                    "Парная модель",
                    "Спред пары и шаблон проверки коинтеграции",
                ),
                ("Carry", "Экран базиса и carry на основе фьючерсной диагностики"),
                ("Фильтр режима", "Режимы волатильности, тренда и ликвидности"),
            ]
            if lang == "ru"
            else [
                ("Momentum", "Rolling return, trend filter, volatility filter"),
                ("Mean Reversion", "Rolling z-score, entry/exit thresholds"),
                ("Pairs Template", "Pairs spread and cointegration research template"),
                ("Carry", "Basis/carry screen from futures basis diagnostics"),
                ("Regime Filter", "Volatility, trend and liquidity regimes"),
            ]
        ),
        columns=["module", "research use"],
    )
    table(modules, height=230, lang=lang)
    if demo_mode:
        show_demo_warning(lang)
        table(load_demo_equity_curve(), height=280, lang=lang)
    else:
        note(
            ui(
                lang,
                "No strategy backtest output is generated by default. Run the strategy "
                "research notebook with real price inputs to avoid fabricated results.",
                "Бэктест стратегий по умолчанию не генерируется. Запустите исследовательский "
                "ноутбук с реальными ценовыми данными, чтобы не показывать выдуманные результаты.",
            )
        )
    section_header(
        ui(lang, "Why This Strategy May Fail", "Почему стратегия может не сработать")
    )
    table(
        pd.DataFrame(
            {
                "failure mode": [
                    "нестабильность эффекта",
                    "высокий оборот",
                    "ограничение ёмкости",
                    "чувствительность к издержкам",
                    "ухудшение ликвидности",
                    "смена рыночного режима",
                    "переобучение",
                ],
                "research implication": [
                    "сигнал может перестать работать",
                    "издержки могут съесть эффект",
                    "оборот ограничивает размер позиции",
                    "малые допущения меняют результат",
                    "инструмент может стать хуже торгуемым",
                    "структура рынка меняется",
                    "подгонка на истории может не повториться",
                ],
            }
        ),
        height=285,
        lang=lang,
    )
    show_methodology_link("strategy-research", lang)
    show_limitations_note(
        ui(
            lang,
            "Templates require out-of-sample validation and cost analysis.",
            "Шаблоны требуют вневыборочной проверки и анализа издержек.",
        ),
        lang,
    )
