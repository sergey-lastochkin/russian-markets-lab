from pathlib import Path


def test_no_silent_fake_data_in_production() -> None:
    allowed = {"tests", "demo", "docs"}
    suspicious = ["np.random", "random.", 'SBER": [', 'GAZP": [', 'LKOH": [']
    root = Path("src/russian_markets_lab")
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        parts = set(path.parts)
        if allowed & parts:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in suspicious:
            if pattern in text:
                offenders.append(f"{path}:{pattern}")
    assert offenders == []
