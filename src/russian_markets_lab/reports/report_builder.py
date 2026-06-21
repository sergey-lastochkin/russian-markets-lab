"""HTML report generation for research outputs."""

from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path

import pandas as pd

from russian_markets_lab.data.io import read_processed_metadata

DISCLAIMER = (
    "Проект предназначен только для исследовательских и образовательных целей. "
    "Он не является инвестиционной рекомендацией, торговым сигналом, брокерским "
    "сервисом или системой отправки реальных заявок. / This project is for "
    "research and educational purposes only. It does not provide investment "
    "advice, trading signals, brokerage functionality, or real-money execution."
)


def _table_html(df: pd.DataFrame, max_rows: int = 25) -> str:
    if df.empty:
        return "<p>Данные не найдены. / No data available.</p>"
    return df.head(max_rows).to_html(index=False, border=0, classes="research-table")


def _bar_chart_html(
    df: pd.DataFrame,
    label_col: str,
    value_col: str,
    title: str,
    max_rows: int = 10,
) -> str:
    if df.empty or label_col not in df.columns or value_col not in df.columns:
        return "<p>График недоступен. / Chart unavailable.</p>"
    chart = df[[label_col, value_col]].copy()
    chart[value_col] = pd.to_numeric(chart[value_col], errors="coerce")
    chart = chart.dropna().sort_values(value_col, ascending=False).head(max_rows)
    if chart.empty:
        return "<p>График недоступен. / Chart unavailable.</p>"
    max_value = chart[value_col].abs().max()
    if max_value == 0:
        return "<p>График недоступен. / Chart unavailable.</p>"
    rows = [f"<h3>{escape(title)}</h3>", '<div class="bars">']
    for _, row in chart.iterrows():
        label = escape(str(row[label_col]))
        value = float(row[value_col])
        width = max(abs(value) / max_value * 100, 2)
        rows.append(
            '<div class="bar-row">'
            f'<span class="bar-label">{label}</span>'
            '<span class="bar-track">'
            f'<span class="bar-fill" style="width:{width:.1f}%"></span>'
            "</span>"
            f'<span class="bar-value">{value:,.4g}</span>'
            "</div>"
        )
    rows.append("</div>")
    return "\n".join(rows)


def _write_html(title: str, body: str, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 40px; color: #17202a; }}
    h1, h2 {{ color: #111827; }}
    .meta {{ color: #52606d; }}
    .research-table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    .research-table th, .research-table td {{ border-bottom: 1px solid #e5e7eb; padding: 8px; text-align: right; }}
    .research-table th:first-child, .research-table td:first-child {{ text-align: left; }}
    .note {{ background: #f8fafc; border-left: 4px solid #64748b; padding: 12px 16px; }}
    .bars {{ margin: 12px 0 28px; }}
    .bar-row {{ align-items: center; display: grid; gap: 10px; grid-template-columns: 140px 1fr 110px; margin: 7px 0; }}
    .bar-label {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .bar-track {{ background: #e5e7eb; border-radius: 4px; display: block; height: 12px; }}
    .bar-fill {{ background: #334155; border-radius: 4px; display: block; height: 12px; }}
    .bar-value {{ color: #475569; font-variant-numeric: tabular-nums; text-align: right; }}
  </style>
</head>
<body>
{body}
</body>
</html>"""
    path.write_text(html, encoding="utf-8")


def _metadata_html(dataset_names: list[str]) -> str:
    rows = []
    for name in dataset_names:
        metadata = read_processed_metadata(name)
        is_demo = bool(metadata.get("is_demo", False))
        rows.append(
            {
                "dataset": name,
                "data_mode": "demo" if is_demo else "processed_cache",
                "generated_at": metadata.get("generated_at"),
                "row_count": metadata.get("row_count"),
                "source": metadata.get("source"),
                "is_demo": is_demo,
                "limitations": "; ".join(metadata.get("limitations", [])[:2]),
            }
        )
    return _table_html(pd.DataFrame(rows))


def build_liquidity_report(
    universe: pd.DataFrame,
    output_path: str,
) -> None:
    """Build an HTML liquidity research report."""

    body = f"""
<h1>Отчёт по ликвидности MOEX / MOEX Liquidity Report</h1>
<p class="meta">Дата формирования / Generated: {date.today().isoformat()}</p>
<h2>Методология / Methodology</h2>
<p>Отчёт ранжирует инструменты по traded value, объёму, качеству данных, liquidity score components и liquidity regime.</p>
<h2>Метаданные датасета / Dataset Metadata</h2>
{_metadata_html(["market_universe", "liquidity_radar"])}
<h2>Графики / Charts</h2>
{_bar_chart_html(universe, "ticker", "avg_value", "Top average traded value")}
{_bar_chart_html(universe, "ticker", "tradability_score", "Tradability score")}
<h2>Таблица ликвидности / Liquidity Table</h2>
{_table_html(universe)}
<h2>Риск-комментарии / Risk Notes</h2>
<p class="note">Ликвидность может резко ухудшаться в стрессовых режимах. Quoted spread используется только при наличии bid/ask; proxy или unavailable spread не являются реальной котировкой. Historical turnover и liquidity regimes - диагностика, а не гарантия исполнения.</p>
<h2>Ограничения / Limitations</h2>
<p>Публичные задержанные данные могут не включать full depth, broker-specific fees и real-time order book dynamics.</p>
<h2>Дисклеймер / Disclaimer</h2>
<p>{DISCLAIMER}</p>
"""
    _write_html("Отчёт по ликвидности MOEX", body, output_path)


def build_derivatives_risk_report(
    basis: pd.DataFrame,
    options: pd.DataFrame,
    risk: pd.DataFrame,
    output_path: str,
) -> None:
    """Build an HTML derivatives and risk research report."""

    body = f"""
<h1>Отчёт по деривативам и риску / Derivatives Risk Report</h1>
<p class="meta">Дата формирования / Generated: {date.today().isoformat()}</p>
<h2>Методология / Methodology</h2>
<p>Отчёт объединяет futures basis deviations with confidence labels, options volatility diagnostics, portfolio stress testing и approximate risk contribution.</p>
<h2>Метаданные датасетов / Dataset Metadata</h2>
{_metadata_html(["futures_basis", "options_chain_features", "risk_snapshot"])}
<h2>Графики / Charts</h2>
{_bar_chart_html(basis, "futures_secid", "annualized_basis", "Annualized futures basis")}
{_bar_chart_html(options, "secid", "implied_volatility", "Top implied volatility")}
<h2>Монитор базиса фьючерсов / Futures Basis Monitor</h2>
{_table_html(basis)}
<h2>Диагностика опционной поверхности / Options Surface Diagnostics</h2>
{_table_html(options)}
<h2>Срез портфельного риска / Portfolio Risk Snapshot</h2>
{_table_html(risk)}
<h2>Риск-комментарии / Risk Notes</h2>
<p class="note">Basis и volatility screens - исследовательская диагностика. Confidence labels отражают качество входных данных и ликвидность, но не являются trading signal. Это не arbitrage claim, не торговая рекомендация и не обещание доходности.</p>
<h2>Ограничения / Limitations</h2>
<p>Model outputs зависят от public data coverage, stale quotes, assumptions about rates/dividends и упрощённых execution costs.</p>
<h2>Дисклеймер / Disclaimer</h2>
<p>{DISCLAIMER}</p>
"""
    _write_html("Отчёт по деривативам и риску", body, output_path)


def build_execution_cost_report(
    execution: pd.DataFrame, output_path: str | Path
) -> None:
    """Build an HTML execution cost research report."""

    body = f"""
<h1>Отчёт по стоимости исполнения / Execution Cost Report</h1>
<p class="meta">Дата формирования / Generated: {date.today().isoformat()}</p>
<h2>Источник данных / Data Source</h2>
<p>Execution comparison строится из processed liquidity assumptions. Это модель диагностики стоимости, не модель отправки реальных заявок.</p>
<h2>Метаданные / Metadata</h2>
{_metadata_html(["execution_comparison"])}
<h2>Графики / Charts</h2>
{_bar_chart_html(execution, "execution_style", "total_cost_bps", "Total cost, bps")}
<h2>Comparison Table</h2>
{_table_html(execution)}
<h2>Ограничения / Limitations</h2>
<p class="note">Модель не учитывает queue position, hidden liquidity, broker routing, market microstructure events и full depth order book.</p>
<h2>Дисклеймер / Disclaimer</h2>
<p>{DISCLAIMER}</p>
"""
    _write_html("Отчёт по стоимости исполнения", body, str(output_path))


def build_project_overview_report(output_path: str | Path) -> None:
    """Build a high-level project overview report."""

    datasets = [
        "market_universe",
        "liquidity_radar",
        "futures_basis",
        "options_chain_features",
        "risk_snapshot",
        "execution_comparison",
    ]
    body = f"""
<h1>Russian Markets Lab - Project Overview</h1>
<p class="meta">Дата формирования / Generated: {date.today().isoformat()}</p>
<h2>Positioning</h2>
<p>Russian Markets Lab - reproducible MOEX market research stack for data ingestion, liquidity diagnostics, derivatives analytics, risk estimation, execution cost modeling and systematic research templates.</p>
<h2>Dataset Metadata</h2>
{_metadata_html(datasets)}
<h2>Methodology and Limitations</h2>
<p>See <code>docs/methodology.md</code>, <code>docs/data_sources.md</code> and <code>docs/limitations.md</code>.</p>
<h2>Disclaimer</h2>
<p>{DISCLAIMER}</p>
"""
    _write_html("Russian Markets Lab - Project Overview", body, str(output_path))
