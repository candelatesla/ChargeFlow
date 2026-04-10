from __future__ import annotations

import pandas as pd

from src.rag.service import answer_query
from src.recommender.service import build_recommendation_snapshot, load_overview_summary, recommend_stations
from src.utils.assets import read_csv_asset


def get_overview_summary() -> dict[str, object]:
    return load_overview_summary()


def get_station_health() -> pd.DataFrame:
    return read_csv_asset("warehouse", "gold_station_health.csv")


def get_station_daily_metrics() -> pd.DataFrame:
    return read_csv_asset("warehouse", "gold_station_daily_metrics.csv")


def get_failure_predictions() -> pd.DataFrame:
    predictions = read_csv_asset("ml", "failure_risk_predictions.csv")
    stations = read_csv_asset("synthetic", "augmented_stations.csv")[["station_id", "station_name", "city", "state"]]
    merged = predictions.merge(stations, on="station_id", how="left")
    return merged


def get_recommendation_snapshot() -> pd.DataFrame:
    build_recommendation_snapshot()
    return read_csv_asset("recommender", "station_recommendations_snapshot.csv")


def get_recommendations_for_state(state: str, top_k: int = 5) -> list[dict[str, object]]:
    return recommend_stations(state, top_k=top_k, max_predicted_failure_probability=0.5)


def run_rag_query(query: str, top_k: int = 3) -> dict[str, object]:
    return answer_query(query, top_k=top_k, use_llm=False)
