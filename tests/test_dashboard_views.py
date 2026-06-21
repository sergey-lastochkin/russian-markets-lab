import pandas as pd

from russian_markets_lab.dashboard.views import prepare_table_display


def test_risk_table_values_are_localized_in_russian() -> None:
    source = pd.DataFrame(
        {
            "metric": ["mean_daily_return", "MOEX index -15%"],
            "method": ["historical arithmetic mean", "simplified scenario shock"],
            "window": ["333 observations", "current equal-weight portfolio"],
            "limitations": [
                "Backward-looking daily sample.",
                "No margin, liquidation, funding or order book impact model.",
            ],
        }
    )

    display = prepare_table_display(source, lang="ru")

    assert display.columns.tolist() == ["Метрика", "Метод", "Выборка", "Ограничения"]
    assert display.iloc[0].tolist() == [
        "средняя доходность за день",
        "среднее по дневной истории",
        "333 дн.",
        "Расчёт основан только на прошлых дневных данных.",
    ]
    assert display.iloc[1].tolist() == [
        "индекс MOEX -15%",
        "заданный стресс-сценарий",
        "текущий портфель с равными весами",
        "Сценарий не учитывает маржу, принудительное закрытие позиций и ликвидность стакана.",
    ]


def test_risk_table_values_remain_english_in_english_ui() -> None:
    source = pd.DataFrame(
        {
            "method": ["historical arithmetic mean"],
            "window": ["333 observations"],
        }
    )

    display = prepare_table_display(source, lang="en")

    assert display.iloc[0].tolist() == [
        "historical arithmetic mean",
        "333 observations",
    ]
