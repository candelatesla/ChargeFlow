from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from functools import lru_cache


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings:
    def __init__(self) -> None:
        env_file_values = _read_env_file(ROOT_DIR / ".env")
        self.nrel_api_key = os.getenv("NREL_API_KEY", env_file_values.get("NREL_API_KEY", "DEMO_KEY"))
        self.eia_api_key = os.getenv("EIA_API_KEY", env_file_values.get("EIA_API_KEY", "DEMO_KEY"))
        self.groq_api_key = os.getenv("GROQ_API_KEY", env_file_values.get("GROQ_API_KEY", ""))
        self.chargeflow_env = os.getenv("CHARGEFLOW_ENV", env_file_values.get("CHARGEFLOW_ENV", "dev"))
        self.chargeflow_log_level = os.getenv(
            "CHARGEFLOW_LOG_LEVEL",
            env_file_values.get("CHARGEFLOW_LOG_LEVEL", "INFO"),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def load_base_config() -> dict[str, Any]:
    config_path = ROOT_DIR / "configs" / "base.yaml"
    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _read_env_file(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    with env_path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values
