"""Streamlit frontend for Russian Markets Lab."""

# ruff: noqa: E402,I001

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

SRC_ROOT = Path(__file__).resolve().parents[2]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from russian_markets_lab.dashboard.components import (  # noqa: E402
    apply_terminal_theme,
    hero,
    show_demo_warning,
)
from russian_markets_lab.dashboard.data_loader import all_dataset_statuses  # noqa: E402
from russian_markets_lab.dashboard.views import (  # noqa: E402
    DATASETS,
    render_execution_tab,
    render_futures_tab,
    render_liquidity_tab,
    render_market_tab,
    render_options_tab,
    render_risk_tab,
    render_sidebar,
    render_strategy_tab,
    render_top_status_bar,
    tab_labels,
)


def main() -> None:
    """Render Streamlit dashboard."""

    st.set_page_config(page_title="Russian Markets Lab", layout="wide")
    apply_terminal_theme()

    statuses = all_dataset_statuses(DATASETS)
    language = st.sidebar.radio(
        "Language / Язык", ["EN", "RU"], index=0, horizontal=True
    )
    lang = "ru" if language == "RU" else "en"
    demo_mode = st.sidebar.checkbox(
        (
            "Использовать демо-данные, если обработанные данные отсутствуют"
            if lang == "ru"
            else "Use demo data when processed data is missing"
        ),
        value=False,
    )
    render_sidebar(demo_mode, statuses, lang)

    hero(
        "Russian Markets Lab",
        (
            "Исследовательский терминал MOEX на публичных/задержанных ISS-данных: "
            "ликвидность, деривативы, риск, исполнение, обработанные датасеты и методология."
            if lang == "ru"
            else "MOEX research terminal built on public/delayed ISS data: liquidity, "
            "derivatives, risk, execution, processed datasets and methodology."
        ),
        "ИССЛЕДОВАНИЕ MOEX" if lang == "ru" else "MOEX RESEARCH",
    )
    render_top_status_bar(demo_mode, statuses, lang)

    if demo_mode:
        show_demo_warning(lang)
    elif not statuses["exists"].any():
        st.info(
            "Обработанные данные отсутствуют. Запустите "
            "`python -m russian_markets_lab.cli build-all`."
            if lang == "ru"
            else "Processed data is missing. Run "
            "`python -m russian_markets_lab.cli build-all`."
        )

    tabs = st.tabs(tab_labels(lang))
    with tabs[0]:
        render_market_tab(lang)
    with tabs[1]:
        render_liquidity_tab(lang)
    with tabs[2]:
        render_futures_tab(lang)
    with tabs[3]:
        render_options_tab(lang)
    with tabs[4]:
        render_risk_tab(lang)
    with tabs[5]:
        render_execution_tab(lang)
    with tabs[6]:
        render_strategy_tab(demo_mode, lang)


if __name__ == "__main__":
    main()
