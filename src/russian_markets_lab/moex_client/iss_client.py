"""Reusable MOEX ISS client."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests


class MOEXISSClientError(Exception):
    """Raised when MOEX ISS requests fail or return invalid payloads."""


class MOEXISSClient:
    """Small requests-based client for the MOEX ISS JSON API."""

    def __init__(
        self,
        base_url: str = "https://iss.moex.com/iss",
        timeout: int = 30,
        retries: int = 3,
        cache_dir: str | Path | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.cache_dir = Path(cache_dir) if cache_dir is not None else None

    def _cache_path(self, path: str, params: dict[str, Any]) -> Path | None:
        if self.cache_dir is None:
            return None
        key_payload = json.dumps(
            {"path": path, "params": params},
            sort_keys=True,
            ensure_ascii=True,
            default=str,
        )
        digest = hashlib.sha256(key_payload.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def get_json(self, path: str, params: dict | None = None) -> dict:
        """Fetch a JSON payload from MOEX ISS."""

        normalized_path = path if path.startswith("/") else f"/{path}"
        url = f"{self.base_url}{normalized_path}"
        query = {"iss.meta": "off"}
        if params:
            query.update(params)

        cache_path = self._cache_path(normalized_path, query)
        if cache_path is not None and cache_path.exists():
            with cache_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if not isinstance(payload, dict):
                raise MOEXISSClientError(
                    "Cached MOEX ISS response is not a JSON object"
                )
            return payload

        last_error: Exception | None = None
        for attempt in range(self.retries):
            try:
                response = self.session.get(url, params=query, timeout=self.timeout)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise MOEXISSClientError("MOEX ISS response is not a JSON object")
                if cache_path is not None:
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    with cache_path.open("w", encoding="utf-8") as handle:
                        json.dump(payload, handle, ensure_ascii=False)
                return payload
            except (requests.RequestException, ValueError, MOEXISSClientError) as exc:
                last_error = exc
                if attempt < self.retries - 1:
                    time.sleep(0.25 * (attempt + 1))

        raise MOEXISSClientError(
            f"MOEX ISS request failed: {last_error}"
        ) from last_error

    @staticmethod
    def parse_table(payload: dict[str, Any], table: str) -> pd.DataFrame:
        """Convert a MOEX JSON table with columns/data into a DataFrame."""

        table_payload = payload.get(table)
        if table_payload is None:
            return pd.DataFrame()
        if not isinstance(table_payload, dict):
            raise MOEXISSClientError(f"MOEX ISS table '{table}' has invalid format")

        if "columns" not in table_payload or "data" not in table_payload:
            raise MOEXISSClientError(f"MOEX ISS table '{table}' misses columns/data")
        columns = table_payload.get("columns")
        data = table_payload.get("data")
        if columns is None or data is None:
            raise MOEXISSClientError(f"MOEX ISS table '{table}' misses columns/data")
        if not data:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(data, columns=columns)

    def get_table(
        self,
        path: str,
        table: str,
        params: dict | None = None,
    ) -> pd.DataFrame:
        """Fetch and parse one MOEX ISS table."""

        payload = self.get_json(path, params=params)
        return self.parse_table(payload, table)

    def get_all_pages(
        self,
        path: str,
        table: str,
        params: dict | None = None,
        start_param: str = "start",
        page_size: int = 100,
        max_pages: int | None = None,
    ) -> pd.DataFrame:
        """Fetch paginated MOEX ISS tables until an empty page is returned."""

        frames: list[pd.DataFrame] = []
        seen_page_signatures: set[tuple[object, ...]] = set()
        start = 0
        page = 0
        base_params = dict(params or {})
        while max_pages is None or page < max_pages:
            page_params = {**base_params, start_param: start}
            df = self.get_table(path, table, params=page_params)
            if df.empty:
                break
            signature = (
                len(df),
                tuple(df.iloc[0].astype(str).tolist()),
                tuple(df.iloc[-1].astype(str).tolist()),
            )
            if signature in seen_page_signatures:
                break
            seen_page_signatures.add(signature)
            frames.append(df)
            if len(df) < page_size:
                break
            start += len(df)
            page += 1

        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)
