"""Plotly chart builders for dashboard tabs."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PLOT_BG = "#080b10"
PAPER_BG = "#080b10"
GRID = "#263241"
TEXT = "#d8dee9"
MUTED = "#8792a2"
ACCENT = "#76a9fa"
ACCENT_2 = "#67c587"
ACCENT_3 = "#d6a84f"
ACCENT_4 = "#d46a6a"
QUALITATIVE = [ACCENT, ACCENT_2, ACCENT_3, ACCENT_4, "#9b8cff"]
FONT_STACK = "Inter, SF Pro Display, Avenir Next, Segoe UI, Arial, sans-serif"


def _ui(lang: str, en: str, ru: str) -> str:
    """Return localized chart copy."""

    return ru if lang == "ru" else en


def _has_columns(df: pd.DataFrame, columns: set[str]) -> bool:
    return not df.empty and columns.issubset(df.columns)


def _format_date_label(value: object, lang: str) -> str:
    """Format date labels for chart legends and hover."""

    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return str(value)
    return parsed.strftime("%d.%m.%Y" if lang == "ru" else "%Y-%m-%d")


def apply_chart_theme(
    fig: go.Figure,
    title: str,
    x_title: str | None = None,
    y_title: str | None = None,
    height: int = 330,
) -> go.Figure:
    """Apply a consistent dark research-terminal Plotly layout."""

    fig.update_layout(
        template="plotly_dark",
        title={"text": title, "font": {"size": 14}, "x": 0.01, "xanchor": "left"},
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font={"color": TEXT, "size": 11, "family": FONT_STACK},
        margin={"l": 42, "r": 16, "t": 54, "b": 78},
        height=height,
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.18,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 10, "color": MUTED},
        },
        colorway=QUALITATIVE,
    )
    fig.update_xaxes(
        title=x_title,
        gridcolor=GRID,
        linecolor=GRID,
        tickfont={"size": 10, "color": MUTED},
        title_font={"size": 11, "color": MUTED},
        zerolinecolor=GRID,
    )
    fig.update_yaxes(
        title=y_title,
        gridcolor=GRID,
        linecolor=GRID,
        tickfont={"size": 10, "color": MUTED},
        title_font={"size": 11, "color": MUTED},
        zerolinecolor=GRID,
    )
    return fig


def market_liquidity_bar(universe: pd.DataFrame, lang: str = "en"):
    """Build market liquidity bar chart."""

    if not _has_columns(universe, {"ticker", "tradability_score"}):
        return None
    data = universe.sort_values("tradability_score", ascending=False).head(25)
    fig = px.bar(
        data, x="ticker", y="tradability_score", color_discrete_sequence=[ACCENT]
    )
    return apply_chart_theme(
        fig,
        _ui(lang, "Top instruments by tradability score", "Топ инструментов по скору"),
        x_title=_ui(lang, "Instrument", "Инструмент"),
        y_title=_ui(lang, "Score", "Скор"),
    )


def market_volatility_scatter(universe: pd.DataFrame, lang: str = "en"):
    """Build volatility versus average traded value scatter."""

    if not _has_columns(universe, {"avg_value", "realized_volatility"}):
        return None
    data = universe.copy()
    color_column = None
    if (
        "tradable_flag" in data.columns
        and data["tradable_flag"].nunique(dropna=True) > 1
    ):
        color_column = "tradability_label"
        data[color_column] = data["tradable_flag"].map(
            {
                True: _ui(lang, "Tradable", "Торгуемый"),
                False: _ui(lang, "Not tradable", "Не торгуемый"),
            }
        )
    fig = px.scatter(
        data,
        x="avg_value",
        y="realized_volatility",
        color=color_column,
        hover_name="ticker" if "ticker" in universe.columns else None,
        color_discrete_sequence=QUALITATIVE,
        labels={
            "avg_value": _ui(lang, "Average traded value", "Средний оборот"),
            "realized_volatility": _ui(
                lang, "Realized volatility", "Реализованная волатильность"
            ),
            "tradability_label": _ui(lang, "Tradability", "Торгуемость"),
            "ticker": _ui(lang, "Ticker", "Тикер"),
        },
    )
    fig.update_traces(marker={"size": 8, "opacity": 0.78, "line": {"width": 0}})
    return apply_chart_theme(
        fig,
        _ui(
            lang,
            "Realized volatility versus average value",
            "Волатильность против оборота",
        ),
        x_title=_ui(lang, "Average traded value", "Средний оборот"),
        y_title=_ui(lang, "Realized volatility", "Реализ. волатильность"),
    )


def liquidity_score_bar(liquidity: pd.DataFrame, lang: str = "en"):
    """Build liquidity score ranking chart."""

    if not _has_columns(liquidity, {"ticker", "liquidity_score"}):
        return None
    data = liquidity.sort_values("liquidity_score", ascending=False).head(25)
    fig = px.bar(
        data, x="ticker", y="liquidity_score", color_discrete_sequence=[ACCENT]
    )
    return apply_chart_theme(
        fig,
        _ui(lang, "Liquidity score ranking", "Рейтинг ликвидности"),
        x_title=_ui(lang, "Instrument", "Инструмент"),
        y_title=_ui(lang, "Score", "Скор"),
    )


def turnover_bar(liquidity: pd.DataFrame, lang: str = "en"):
    """Build turnover chart."""

    value_column = (
        "avg_daily_value" if "avg_daily_value" in liquidity.columns else "turnover"
    )
    if not _has_columns(liquidity, {"ticker", value_column}):
        return None
    data = liquidity.sort_values(value_column, ascending=False).head(25)
    fig = px.bar(
        data,
        x="ticker",
        y=value_column,
        color_discrete_sequence=[ACCENT_2],
        labels={
            "ticker": _ui(lang, "Instrument", "Инструмент"),
            value_column: _ui(lang, "Average daily value", "Среднедневной оборот"),
        },
    )
    if value_column == "avg_daily_value":
        fig.update_traces(
            hovertemplate=(
                f"{_ui(lang, 'Instrument', 'Инструмент')}: %{{x}}<br>"
                f"{_ui(lang, 'Average daily value', 'Среднедневной оборот')}: "
                "%{y:,.0f} RUB<extra></extra>"
            )
        )
    return apply_chart_theme(
        fig,
        _ui(lang, "Average daily traded value", "Среднедневной оборот"),
        x_title=_ui(lang, "Instrument", "Инструмент"),
        y_title=_ui(lang, "RUB", "RUB"),
    )


def futures_basis_bar(basis: pd.DataFrame, lang: str = "en"):
    """Build annualized futures basis chart."""

    if not _has_columns(basis, {"futures_secid", "annualized_basis"}):
        return None
    signal_colors = {
        "cheap": ACCENT_2,
        "fair": ACCENT,
        "rich": ACCENT_4,
        "unknown": MUTED,
    }
    fig = px.bar(
        basis,
        x="futures_secid",
        y="annualized_basis",
        color="signal" if "signal" in basis.columns else None,
        color_discrete_map=signal_colors,
    )
    return apply_chart_theme(
        fig,
        _ui(lang, "Annualized futures basis", "Годовой фьючерсный базис"),
        x_title=_ui(lang, "Futures contract", "Фьючерс"),
        y_title=_ui(lang, "Annualized basis", "Годовой базис"),
    )


def options_smile_chart(chain: pd.DataFrame, lang: str = "en"):
    """Build implied volatility smile chart."""

    if not _has_columns(chain, {"strike", "implied_volatility", "expiration"}):
        return None
    clean = chain.dropna(subset=["implied_volatility"]).copy()
    if clean.empty:
        return None
    clean["expiration_dt"] = pd.to_datetime(clean["expiration"], errors="coerce")
    expiries = clean["expiration_dt"].dropna().sort_values().drop_duplicates().head(5)
    if not expiries.empty:
        clean = clean[clean["expiration_dt"].isin(expiries)]
    clean["expiration_label"] = clean["expiration"].map(
        lambda value: _format_date_label(value, lang)
    )
    clean = clean.sort_values(["expiration_label", "strike"])
    fig = px.line(
        clean.head(500),
        x="strike",
        y="implied_volatility",
        color="expiration_label",
        markers=True,
        color_discrete_sequence=QUALITATIVE,
        labels={
            "strike": _ui(lang, "Strike", "Страйк"),
            "implied_volatility": _ui(
                lang, "Implied volatility", "Подразумеваемая волатильность"
            ),
            "expiration_label": _ui(lang, "Expiration", "Экспирация"),
        },
    )
    fig.update_traces(
        hovertemplate=(
            f"{_ui(lang, 'Strike', 'Страйк')}: %{{x}}<br>"
            f"{_ui(lang, 'Implied volatility', 'Подразумеваемая волатильность')}: "
            "%{y:.2%}<extra></extra>"
        )
    )
    themed = apply_chart_theme(
        fig,
        _ui(
            lang,
            "Implied volatility smile",
            "Улыбка подразумеваемой волатильности",
        ),
        x_title=_ui(lang, "Strike", "Страйк"),
        y_title=_ui(lang, "Implied volatility", "Подразумеваемая волатильность"),
    )
    themed.update_layout(
        legend_title_text=_ui(lang, "Expiration", "Экспирация"),
        height=430,
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.2,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 10, "color": MUTED, "family": FONT_STACK},
        },
        margin={"l": 58, "r": 18, "t": 58, "b": 112},
    )
    return themed


def options_surface_heatmap(chain: pd.DataFrame, lang: str = "en"):
    """Build moneyness by expiry implied volatility heatmap."""

    if not _has_columns(chain, {"moneyness", "time_to_expiry", "implied_volatility"}):
        return None
    clean = chain.dropna(subset=["moneyness", "time_to_expiry", "implied_volatility"])
    if clean.empty:
        return None
    fig = px.density_heatmap(
        clean,
        x="moneyness",
        y="time_to_expiry",
        z="implied_volatility",
        histfunc="avg",
        color_continuous_scale=["#111923", ACCENT, ACCENT_3],
        labels={
            "moneyness": _ui(lang, "Moneyness", "Денежность"),
            "time_to_expiry": _ui(lang, "Time to expiry", "Срок до экспирации"),
            "implied_volatility": _ui(
                lang, "Implied volatility", "Подразумеваемая волатильность"
            ),
        },
    )
    fig.update_traces(
        hovertemplate=(
            f"{_ui(lang, 'Moneyness', 'Денежность')}: %{{x}}<br>"
            f"{_ui(lang, 'Time to expiry', 'Срок до экспирации')}: %{{y}}<br>"
            f"{_ui(lang, 'Average IV', 'Средняя подраз. вол.')}: %{{z:.2%}}<extra></extra>"
        )
    )
    fig.update_coloraxes(
        colorbar_title_text=_ui(lang, "Average IV", "Средняя подраз. вол.")
    )
    return apply_chart_theme(
        fig,
        _ui(
            lang,
            "Implied volatility surface proxy",
            "Поверхность подразумеваемой волатильности",
        ),
        x_title=_ui(lang, "Moneyness", "Денежность"),
        y_title=_ui(lang, "Time to expiry", "Срок до экспирации, лет"),
    )


def risk_correlation_heatmap(corr: pd.DataFrame):
    """Build correlation heatmap."""

    if corr.empty:
        return None
    fig = px.imshow(corr, color_continuous_scale="RdBu", zmin=-1, zmax=1)
    return apply_chart_theme(fig, "Correlation matrix", height=420)


def drawdown_chart(drawdowns: pd.Series):
    """Build drawdown chart."""

    if drawdowns.empty:
        return None
    fig = px.line(drawdowns, color_discrete_sequence=[ACCENT_4])
    return apply_chart_theme(fig, "Drawdown", x_title="Date", y_title="Drawdown")


def execution_cost_bar(execution: pd.DataFrame, lang: str = "en"):
    """Build execution total cost chart."""

    if not _has_columns(execution, {"execution_style", "total_cost_bps"}):
        return None
    data = execution.copy()
    if lang == "ru":
        data["execution_style_label"] = (
            data["execution_style"]
            .map(
                {
                    "market": "рыночная",
                    "limit": "лимитная",
                    "twap": "TWAP",
                    "vwap": "VWAP",
                }
            )
            .fillna(data["execution_style"])
        )
        if "execution_risk" in data.columns:
            data["execution_risk_label"] = (
                data["execution_risk"]
                .map(
                    {
                        "low fill risk, higher immediacy cost": "срочность",
                        "fill uncertainty": "неопределённость исполнения",
                        "schedule risk": "риск расписания",
                        "volume profile risk": "риск профиля объёма",
                    }
                )
                .fillna(data["execution_risk"])
            )
    else:
        data["execution_style_label"] = data["execution_style"]
        if "execution_risk" in data.columns:
            data["execution_risk_label"] = data["execution_risk"]
    fig = px.bar(
        data,
        x="execution_style_label",
        y="total_cost_bps",
        color=(
            "execution_risk_label" if "execution_risk_label" in data.columns else None
        ),
        color_discrete_sequence=QUALITATIVE,
        labels={
            "execution_style_label": _ui(lang, "Execution style", "Стиль исполнения"),
            "total_cost_bps": _ui(lang, "Total cost, bps", "Полные издержки, б.п."),
            "execution_risk_label": _ui(lang, "Execution risk", "Риск исполнения"),
        },
    )
    return apply_chart_theme(
        fig,
        _ui(lang, "Execution cost comparison", "Сравнение издержек исполнения"),
        x_title=_ui(lang, "Execution style", "Стиль исполнения"),
        y_title=_ui(lang, "Total cost, bps", "Полные издержки, б.п."),
    )


def empty_figure():
    """Return an empty Plotly figure."""

    return apply_chart_theme(go.Figure(), "No data available")
