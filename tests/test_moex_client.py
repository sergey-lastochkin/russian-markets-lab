import pandas as pd
import pytest

from russian_markets_lab.moex_client.iss_client import MOEXISSClient, MOEXISSClientError


def test_moex_table_parser() -> None:
    payload = {
        "securities": {"columns": ["SECID", "SHORTNAME"], "data": [["SBER", "Sber"]]}
    }
    df = MOEXISSClient.parse_table(payload, "securities")
    assert list(df.columns) == ["SECID", "SHORTNAME"]
    assert df.iloc[0]["SECID"] == "SBER"


def test_empty_table_handling() -> None:
    payload = {"securities": {"columns": ["SECID"], "data": []}}
    df = MOEXISSClient.parse_table(payload, "securities")
    assert isinstance(df, pd.DataFrame)
    assert df.empty
    assert list(df.columns) == ["SECID"]


def test_invalid_response_handling() -> None:
    payload = {"securities": {"columns": ["SECID"]}}
    with pytest.raises(MOEXISSClientError):
        MOEXISSClient.parse_table(payload, "securities")


def test_missing_table_returns_empty() -> None:
    df = MOEXISSClient.parse_table({}, "securities")
    assert df.empty


def test_repeated_page_breaks_pagination() -> None:
    class RepeatingClient(MOEXISSClient):
        def __init__(self) -> None:
            super().__init__()
            self.calls = 0

        def get_table(
            self, path: str, table: str, params: dict | None = None
        ) -> pd.DataFrame:
            self.calls += 1
            return pd.DataFrame({"SECID": ["SBER", "GAZP"]})

    client = RepeatingClient()
    result = client.get_all_pages("/ignored.json", "securities", page_size=1)
    assert len(result) == 2
    assert client.calls == 2


def test_get_json_uses_local_cache(tmp_path) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"securities": {"columns": ["SECID"], "data": [["SBER"]]}}

    class FakeSession:
        def __init__(self) -> None:
            self.calls = 0

        def get(self, *args, **kwargs) -> FakeResponse:
            self.calls += 1
            return FakeResponse()

    client = MOEXISSClient(cache_dir=tmp_path)
    fake_session = FakeSession()
    client.session = fake_session

    first = client.get_json("/securities.json", params={"start": 0})
    second = client.get_json("/securities.json", params={"start": 0})

    assert first == second
    assert fake_session.calls == 1
    assert len(list(tmp_path.glob("*.json"))) == 1
