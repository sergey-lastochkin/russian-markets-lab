"""Reusable Streamlit dashboard components."""

from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st


def apply_terminal_theme() -> None:
    """Apply a compact dark research-terminal visual theme."""

    st.markdown(
        """
<style>
  :root {
    --rml-bg: #080b10;
    --rml-panel: #0d131c;
    --rml-panel-2: #111923;
    --rml-border: #263241;
    --rml-text: #d8dee9;
    --rml-muted: #8792a2;
    --rml-accent: #76a9fa;
    --rml-warn: #d6a84f;
    --rml-good: #67c587;
    --rml-bad: #d46a6a;
    --rml-font: "Inter", "SF Pro Display", "Avenir Next", "Segoe UI", Arial, sans-serif;
    --rml-mono: "IBM Plex Mono", "SF Mono", "Menlo", "Consolas", monospace;
  }
  @keyframes rmlFadeUp {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  html,
  body {
    background: #070910;
  }
  .stApp {
    background: transparent;
    color: var(--rml-text);
    font-family: var(--rml-font);
  }
  [data-testid="stAppViewContainer"] {
    background:
      linear-gradient(180deg, rgba(8, 11, 16, 0.9), rgba(8, 11, 16, 0.98)),
      radial-gradient(circle at 18% 0%, rgba(72, 91, 135, 0.18), transparent 32%),
      radial-gradient(circle at 82% 18%, rgba(45, 64, 100, 0.13), transparent 30%),
      #080b10;
    overflow-x: hidden;
    overflow-y: auto;
    position: relative;
  }
  [data-testid="stAppViewContainer"]::before {
    background:
      linear-gradient(90deg, rgba(120, 140, 176, 0.035) 1px, transparent 1px),
      linear-gradient(180deg, rgba(120, 140, 176, 0.03) 1px, transparent 1px);
    background-size: 72px 72px;
    content: "";
    inset: -10%;
    opacity: 0.65;
    pointer-events: none;
    position: fixed;
    z-index: 0;
  }
  [data-testid="stSidebar"],
  [data-testid="stAppViewContainer"] .main {
    position: relative;
    z-index: 1;
  }
  @media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      scroll-behavior: auto !important;
      transition-duration: 0.01ms !important;
    }
  }
  html, body, [class^="st-"], [class*=" st-"],
  [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
  [data-testid="stHeader"], [data-testid="stToolbar"],
  .stApp, .stApp p, .stApp span, .stApp div, .stApp button,
  .stApp label, .stApp input, .stApp textarea, .stApp table,
  .stApp th, .stApp td {
    font-family: var(--rml-font) !important;
  }
  .stApp *:not(code):not(pre):not(kbd) {
    font-family: var(--rml-font) !important;
  }
  [data-testid="stSidebar"] {
    background: rgba(7, 10, 15, 0.88);
    backdrop-filter: blur(18px);
    border-right: 1px solid var(--rml-border);
    height: 100vh;
    max-height: 100vh;
    overflow-y: auto !important;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
  }
  [data-testid="stSidebar"] > div,
  [data-testid="stSidebarContent"] {
    max-height: 100vh;
    overflow-y: auto !important;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
  }
  [data-testid="collapsedControl"],
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stStatusWidget"],
  [data-testid="stDecoration"],
  [data-testid="stConnectionStatus"],
  .stDeployButton,
  header {
    display: none !important;
    visibility: hidden !important;
  }
  [data-testid="stSidebar"] * {
    font-size: 0.88rem;
  }
  .block-container {
    padding-top: 1.1rem;
    padding-bottom: 2rem;
    max-width: 1480px;
  }
  h1 {
    font-size: 1.55rem !important;
    font-weight: 650 !important;
    letter-spacing: 0 !important;
    margin-bottom: 0.1rem !important;
  }
  h2, h3 {
    letter-spacing: 0 !important;
  }
  div[data-testid="stCaptionContainer"], .stCaption {
    color: var(--rml-muted) !important;
    font-size: 0.78rem !important;
  }
  .rml-terminal-title {
    border-bottom: 1px solid var(--rml-border);
    color: var(--rml-text);
    font-size: 0.86rem;
    font-weight: 700;
    letter-spacing: 0;
    margin: 0.55rem 0 0.7rem;
    padding-bottom: 0.4rem;
    text-transform: uppercase;
  }
  .rml-hero {
    background: transparent;
    border-bottom: 1px solid var(--rml-border);
    border-radius: 0;
    display: grid;
    gap: 0.35rem;
    margin: 0 0 0.95rem;
    padding: 0.2rem 0 0.95rem;
    animation: rmlFadeUp 0.22s ease-out both;
  }
  .rml-hero-top {
    align-items: baseline;
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
  }
  .rml-hero-title {
    color: var(--rml-text);
    font-size: 1.48rem;
    font-weight: 760;
    letter-spacing: 0;
    line-height: 1.15;
  }
  .rml-hero-badge {
    border: 1px solid rgba(103, 197, 135, 0.45);
    border-radius: 999px;
    color: var(--rml-good);
    font-size: 0.68rem;
    font-weight: 720;
    padding: 0.13rem 0.48rem;
    text-transform: uppercase;
  }
  .rml-hero-subtitle {
    color: var(--rml-muted);
    font-size: 0.86rem;
    line-height: 1.45;
  }
  .rml-hero-credit {
    border: 1px solid rgba(118, 169, 250, 0.38);
    border-radius: 999px;
    color: #a8b2c1;
    font-size: 0.72rem;
    font-weight: 650;
    margin-left: auto;
    padding: 0.14rem 0.52rem;
  }
  @media (max-width: 800px) {
    .rml-hero-credit {
      margin-left: 0;
    }
  }
  .rml-section {
    color: var(--rml-text);
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0;
    margin: 1.1rem 0 0.45rem;
  }
  .rml-note {
    animation: rmlFadeUp 0.22s ease-out both;
    background: rgba(11, 17, 25, 0.92);
    backdrop-filter: blur(8px);
    border: 1px solid var(--rml-border);
    color: var(--rml-muted);
    font-size: 0.82rem;
    line-height: 1.45;
    padding: 0.7rem 0.85rem;
  }
  .rml-metadata {
    animation: rmlFadeUp 0.22s ease-out both;
    background: rgba(9, 13, 19, 0.92);
    backdrop-filter: blur(8px);
    border: 1px solid var(--rml-border);
    border-radius: 6px;
    color: var(--rml-muted);
    display: grid;
    gap: 0.45rem 0.85rem;
    grid-template-columns: minmax(110px, 0.7fr) repeat(auto-fit, minmax(180px, 1fr));
    margin: 0.8rem 0 0.45rem;
    padding: 0.62rem 0.72rem;
  }
  .rml-metadata-title {
    color: var(--rml-text);
    font-size: 0.76rem;
    font-weight: 720;
    margin-right: 0.2rem;
    text-transform: uppercase;
  }
  .rml-metadata-item {
    color: var(--rml-muted);
    font-size: 0.76rem;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .rml-metadata-item b {
    color: #a8b2c1;
    font-weight: 650;
  }
  .rml-metrics {
    display: grid;
    gap: 0.65rem;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    margin: 0.75rem 0 1rem;
  }
  .rml-card {
    align-content: center;
    animation: rmlFadeUp 0.22s ease-out both;
    background:
      linear-gradient(180deg, rgba(17, 25, 35, 0.94), rgba(10, 15, 23, 0.94));
    backdrop-filter: blur(8px);
    border: 1px solid rgba(63, 79, 103, 0.9);
    border-radius: 6px;
    display: grid;
    gap: 0.18rem;
    grid-template-rows: auto auto auto;
    min-height: 104px;
    padding: 0.8rem 0.8rem;
    transition: border-color 0.16s ease, box-shadow 0.16s ease, transform 0.16s ease;
  }
  .rml-card:hover {
    border-color: rgba(118, 169, 250, 0.62);
    box-shadow: 0 8px 20px rgba(8, 15, 28, 0.28);
    transform: translateY(-1px);
  }
  .rml-card-label {
    color: var(--rml-muted);
    font-size: 0.68rem;
    font-weight: 650;
    letter-spacing: 0;
    text-transform: uppercase;
  }
  .rml-card-value {
    color: var(--rml-text);
    font-size: 1.15rem;
    font-variant-numeric: tabular-nums;
    font-weight: 720;
    line-height: 1.18;
    white-space: pre-line;
  }
  .rml-card-caption {
    color: var(--rml-muted);
    font-size: 0.72rem;
    line-height: 1.2;
    margin-top: 0.12rem;
  }
  .rml-statusbar {
    display: grid;
    gap: 0.55rem;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    margin: 0.8rem 0 1.2rem;
  }
  .rml-pill {
    border: 1px solid var(--rml-border);
    border-radius: 999px;
    color: var(--rml-text);
    display: inline-block;
    font-size: 0.72rem;
    margin: 0.12rem 0.15rem 0.12rem 0;
    padding: 0.16rem 0.48rem;
  }
  .rml-pill.good { border-color: rgba(103, 197, 135, 0.55); color: var(--rml-good); }
  .rml-pill.warn { border-color: rgba(214, 168, 79, 0.55); color: var(--rml-warn); }
  .rml-pill.bad { border-color: rgba(212, 106, 106, 0.55); color: var(--rml-bad); }
  .rml-status-list {
    display: grid;
    gap: 0.32rem;
    margin: 0.65rem 0 0.75rem;
  }
  .rml-status-row {
    align-items: start;
    background: rgba(9, 13, 19, 0.86);
    backdrop-filter: blur(12px);
    border: 1px solid var(--rml-border);
    border-left: 3px solid var(--rml-border);
    border-radius: 5px;
    display: grid;
    gap: 0.08rem;
    grid-template-columns: 1fr;
    padding: 0.38rem 0.5rem;
  }
  .rml-status-label {
    color: var(--rml-muted);
    font-size: 0.72rem;
    font-weight: 650;
    min-width: 0;
  }
  .rml-status-value {
    color: var(--rml-text);
    font-size: 0.72rem;
    font-weight: 720;
    line-height: 1.25;
    text-align: left;
    white-space: normal;
  }
  .rml-status-row.good { border-left-color: var(--rml-good); }
  .rml-status-row.warn { border-left-color: var(--rml-warn); }
  .rml-status-row.bad { border-left-color: var(--rml-bad); }
  .rml-status-row.good .rml-status-value { color: var(--rml-good); }
  .rml-status-row.warn .rml-status-value { color: var(--rml-warn); }
  .rml-status-row.bad .rml-status-value { color: var(--rml-bad); }
  code {
    background: #111923 !important;
    border: 1px solid #243246;
    color: #c8d4e4 !important;
    font-family: var(--rml-mono) !important;
    padding: 0.08rem 0.24rem !important;
  }
  div[data-testid="stDataFrame"] {
    border: 1px solid var(--rml-border);
    border-radius: 6px;
  }
  div[data-testid="stDataFrame"] * {
    font-size: 0.78rem;
  }
  .js-plotly-plot .modebar {
    background: rgba(8, 11, 16, 0.78) !important;
    border: 1px solid rgba(38, 50, 65, 0.82) !important;
    border-radius: 6px !important;
    padding: 0.12rem 0.18rem !important;
  }
  .js-plotly-plot .modebar-btn {
    opacity: 0.72 !important;
  }
  .js-plotly-plot .modebar-btn:hover {
    background: rgba(118, 169, 250, 0.14) !important;
    opacity: 1 !important;
  }
  .js-plotly-plot .modebar-btn svg path {
    fill: #d8dee9 !important;
  }
  .rml-table-wrap {
    animation: rmlFadeUp 0.22s ease-out both;
    backdrop-filter: blur(8px);
    border: 1px solid var(--rml-border);
    border-radius: 6px;
    overflow: auto;
    margin: 0.4rem 0 0.9rem;
    background: rgba(9, 13, 19, 0.84);
  }
  .rml-table {
    border-collapse: collapse;
    font-size: 0.8rem;
    font-variant-numeric: tabular-nums;
    min-width: 100%;
    width: 100%;
  }
  .rml-table th {
    background: #121821;
    border-bottom: 1px solid var(--rml-border);
    color: #a8b2c1;
    font-size: 0.72rem;
    font-weight: 720;
    padding: 0.58rem 0.7rem;
    position: sticky;
    top: 0;
    text-align: left;
    text-transform: uppercase;
    white-space: nowrap;
    z-index: 1;
  }
  .rml-table td {
    border-bottom: 1px solid rgba(38, 50, 65, 0.72);
    color: var(--rml-text);
    padding: 0.52rem 0.7rem;
    white-space: nowrap;
  }
  .rml-table tr:nth-child(even) td {
    background: rgba(255, 255, 255, 0.012);
  }
  .rml-table tr:hover td {
    background: rgba(118, 169, 250, 0.08);
  }
  .rml-table td:not(:first-child):not(:nth-child(2)) {
    text-align: right;
  }
  .rml-info {
    align-items: center;
    border: 1px solid rgba(118, 169, 250, 0.5);
    border-radius: 50%;
    color: var(--rml-accent);
    cursor: help;
    display: inline-flex;
    font-size: 0.62rem;
    font-weight: 800;
    height: 0.92rem;
    justify-content: center;
    line-height: 1;
    margin-left: 0.34rem;
    position: relative;
    text-transform: none;
    vertical-align: 0.08rem;
    width: 0.92rem;
  }
  .rml-info::after {
    background: #111923;
    border: 1px solid var(--rml-border);
    border-radius: 6px;
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.35);
    color: var(--rml-text);
    content: attr(data-tip);
    font-size: 0.74rem;
    font-weight: 500;
    left: 50%;
    line-height: 1.35;
    opacity: 0;
    padding: 0.55rem 0.65rem;
    pointer-events: none;
    position: absolute;
    text-align: left;
    text-transform: none;
    top: 1.25rem;
    transform: translateX(-50%) translateY(-4px);
    transition: opacity 0.12s ease, transform 0.12s ease;
    visibility: hidden;
    white-space: normal;
    width: 220px;
    z-index: 50;
  }
  .rml-info:hover::after {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
    visibility: visible;
  }
  div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    align-items: center;
    border-bottom: 1px solid rgba(38, 50, 65, 0.78);
    display: flex;
    gap: 1.5rem;
    min-height: 2.5rem;
  }
  div[data-testid="stTabs"] [data-baseweb="tab"] {
    align-items: center;
    display: inline-flex;
    font-size: 0.92rem;
    font-weight: 620;
    height: 2.5rem;
    justify-content: center;
    line-height: 1;
    margin: 0;
    padding: 0 0 0.55rem;
    transition: color 0.14s ease, transform 0.14s ease;
  }
  div[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    transform: translateY(-1px);
  }
  div[data-testid="stTabs"] [data-baseweb="tab"] p {
    font-size: 0.92rem !important;
    line-height: 1 !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: #ff5b5b;
    height: 2px;
  }
  div[data-testid="stAlert"] {
    background: #0c131c;
    border: 1px solid var(--rml-border);
    color: var(--rml-text);
  }
</style>
""",
        unsafe_allow_html=True,
    )


def info_icon(text: str | None) -> str:
    """Return a small hover information marker."""

    if not text:
        return ""
    return f'<span class="rml-info" data-tip="{escape(text)}">i</span>'


def section_header(
    title: str, caption: str | None = None, info: str | None = None
) -> None:
    """Render a compact professional section header."""

    st.markdown(
        f'<div class="rml-section">{escape(title)}{info_icon(info)}</div>',
        unsafe_allow_html=True,
    )
    if caption:
        st.caption(caption)


def terminal_title(title: str, container=st) -> None:
    """Render a sidebar or panel title."""

    container.markdown(
        f'<div class="rml-terminal-title">{escape(title)}</div>',
        unsafe_allow_html=True,
    )


def hero(
    title: str, subtitle: str, badge: str | None = None, credit: str | None = None
) -> None:
    """Render the dashboard title area."""

    badge_html = f'<span class="rml-hero-badge">{escape(badge)}</span>' if badge else ""
    credit_html = (
        f'<span class="rml-hero-credit">{escape(credit)}</span>' if credit else ""
    )
    st.markdown(
        '<div class="rml-hero">'
        '<div class="rml-hero-top">'
        f'<div class="rml-hero-title">{escape(title)}</div>{badge_html}{credit_html}'
        "</div>"
        f'<div class="rml-hero-subtitle">{escape(subtitle)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def metric_cards(cards: list[tuple]) -> None:
    """Render compact metric cards."""

    html_cards = []
    for card in cards:
        label, value, caption = card[:3]
        info = card[3] if len(card) > 3 else None
        caption_html = (
            f'<div class="rml-card-caption">{escape(str(caption))}</div>'
            if caption
            else ""
        )
        html_cards.append(
            '<div class="rml-card">'
            f'<div class="rml-card-label">{escape(str(label))}{info_icon(str(info) if info else None)}</div>'
            f'<div class="rml-card-value">{escape(str(value))}</div>'
            f"{caption_html}"
            "</div>"
        )
    st.markdown(
        f'<div class="rml-metrics">{"".join(html_cards)}</div>',
        unsafe_allow_html=True,
    )


def status_pills(items: list[tuple[str, str, str]], container=st) -> None:
    """Render compact status pills.

    Each item is ``(label, value, status)`` where status is good, warn, bad or neutral.
    """

    html = []
    for label, value, status in items:
        css = status if status in {"good", "warn", "bad"} else ""
        html.append(
            f'<span class="rml-pill {css}">{escape(label)}: {escape(value)}</span>'
        )
    container.markdown("".join(html), unsafe_allow_html=True)


def status_rows(items: list[tuple[str, str, str]], container=st) -> None:
    """Render compact sidebar status rows."""

    rows = []
    for label, value, status in items:
        css = status if status in {"good", "warn", "bad"} else ""
        rows.append(
            f'<div class="rml-status-row {css}">'
            f'<span class="rml-status-label">{escape(label)}</span>'
            f'<span class="rml-status-value">{escape(value)}</span>'
            "</div>"
        )
    container.markdown(
        f'<div class="rml-status-list">{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


def note(text: str) -> None:
    """Render a dense research note."""

    st.markdown(f'<div class="rml-note">{escape(text)}</div>', unsafe_allow_html=True)


def show_dataset_metadata(metadata: dict, lang: str = "ru") -> None:
    """Render dataset metadata in an expander."""

    if not metadata:
        text = (
            "Метаданные датасета не найдены."
            if lang == "ru"
            else "Dataset metadata not found."
        )
        st.markdown(
            f'<div class="rml-metadata"><span class="rml-metadata-title">{escape(text)}</span></div>',
            unsafe_allow_html=True,
        )
        return
    title = "Метаданные" if lang == "ru" else "Metadata"
    source_label = "Источник" if lang == "ru" else "Source"
    rows_label = "Строки" if lang == "ru" else "Rows"
    generated_label = "Обновлено" if lang == "ru" else "Generated"
    demo_label = "Демо" if lang == "ru" else "Demo"
    source = str(metadata.get("source", "н/д"))
    if lang == "ru":
        source = {
            "MOEX ISS public/delayed data": "MOEX ISS, публичные/задержанные данные",
            "Processed from liquidity snapshot assumptions": "Расчёт по срезу ликвидности",
            "Derived from processed market data": "Расчёт по обработанным рыночным данным",
        }.get(source, source)
    demo_value = metadata.get("is_demo", False)
    demo_text = (
        ("Да" if bool(demo_value) else "Нет") if lang == "ru" else str(bool(demo_value))
    )
    generated_raw = metadata.get("generated_at")
    generated_dt = pd.to_datetime(generated_raw, errors="coerce", utc=True)
    if pd.isna(generated_dt):
        generated = str(generated_raw or ("н/д" if lang == "ru" else "n/a"))
    else:
        generated = generated_dt.tz_convert("Europe/Moscow").strftime(
            "%d.%m.%Y %H:%M МСК" if lang == "ru" else "%Y-%m-%d %H:%M MSK"
        )
    html = (
        '<div class="rml-metadata">'
        f'<span class="rml-metadata-title">{escape(title)}</span>'
        f'<span class="rml-metadata-item"><b>{source_label}:</b> {escape(source)}</span>'
        f'<span class="rml-metadata-item"><b>{rows_label}:</b> {escape(str(metadata.get("row_count", "н/д")))}</span>'
        f'<span class="rml-metadata-item"><b>{generated_label}:</b> {escape(generated)}</span>'
        f'<span class="rml-metadata-item"><b>{demo_label}:</b> {escape(demo_text)}</span>'
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def show_missing_data_message(dataset_name: str, lang: str = "ru") -> None:
    """Show missing data message."""

    if lang == "ru":
        st.info(
            f"Датасет `{dataset_name}` отсутствует или пуст. "
            "Сгенерируйте обработанные данные командой "
            "`python -m russian_markets_lab.cli build-all`."
        )
    else:
        st.info(
            f"Dataset `{dataset_name}` is missing or empty. "
            "Generate processed data with "
            "`python -m russian_markets_lab.cli build-all`."
        )


def show_demo_warning(lang: str = "ru") -> None:
    """Show explicit demo mode warning."""

    if lang == "ru":
        st.warning(
            "Демо-режим включён. Показанные значения могут быть иллюстративными "
            "и не являются реальным исследовательским выводом."
        )
    else:
        st.warning(
            "Demo mode is enabled. Displayed values may be illustrative and are not real market research output."
        )


def show_methodology_link(section: str, lang: str = "ru") -> None:
    """Show methodology references for a dashboard section."""

    if lang == "ru":
        st.caption(
            f"Методология: docs/methodology.md#{section}. "
            "Источники данных: docs/data_sources.md. Ограничения: docs/limitations.md."
        )
    else:
        st.caption(
            f"Methodology: docs/methodology.md#{section}. "
            "Data sources: docs/data_sources.md. Limitations: docs/limitations.md."
        )


def show_limitations_note(text: str, lang: str = "ru") -> None:
    """Show a concise limitations note."""

    prefix = "Ограничения" if lang == "ru" else "Limitations"
    st.caption(f"{prefix}: {text}")
