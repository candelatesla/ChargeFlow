from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.utils.config import ROOT_DIR


def asset_csv_path(category: str, file_name: str) -> Path:
    processed_path = ROOT_DIR / "data" / "processed" / category / file_name
    if processed_path.exists():
        return processed_path

    demo_path = ROOT_DIR / "demo_assets" / category / file_name
    if demo_path.exists():
        return demo_path

    raise FileNotFoundError(f"Could not find asset {file_name} in processed or demo assets for category {category}.")


def read_csv_asset(category: str, file_name: str) -> pd.DataFrame:
    return pd.read_csv(asset_csv_path(category, file_name))


def read_json_asset(category: str, file_name: str) -> dict[str, object]:
    path = ROOT_DIR / "data" / "processed" / category / file_name
    if not path.exists():
        path = ROOT_DIR / "demo_assets" / category / file_name
    if not path.exists():
        raise FileNotFoundError(f"Could not find JSON asset {file_name} in processed or demo assets for category {category}.")
    return json.loads(path.read_text(encoding="utf-8"))
