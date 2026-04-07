from __future__ import annotations

from pathlib import Path

import json
import pandas as pd

from src.utils.assets import read_csv_asset, read_json_asset
from src.utils.filesystem import recommender_data_root


def build_recommendation_snapshot() -> Path:
    health = read_csv_asset("warehouse", "gold_station_health.csv")
    daily = read_csv_asset("warehouse", "gold_station_daily_metrics.csv")
    failure_predictions = read_csv_asset("ml", "failure_risk_predictions.csv")
    stations = read_csv_asset("synthetic", "augmented_stations.csv")

    latest_daily = (
        daily.sort_values("metric_date")
        .groupby("station_id", as_index=False)
        .tail(1)
        .rename(columns={"avg_queue_minutes": "latest_avg_queue_minutes", "session_count": "latest_session_count"})
    )
    latest_failure = (
        failure_predictions.sort_values("metric_date")
        .groupby("station_id", as_index=False)
        .tail(1)
        .rename(columns={"predicted_failure_probability": "predicted_failure_probability"})
    )

    df = stations.merge(health, on=["station_id", "state"], how="left")
    df = df.merge(
        latest_daily[["station_id", "metric_date", "latest_avg_queue_minutes", "latest_session_count"]],
        on="station_id",
        how="left",
    )
    df = df.merge(
        latest_failure[["station_id", "metric_date", "predicted_failure_probability"]],
        on="station_id",
        how="left",
        suffixes=("", "_failure"),
    )

    numeric_columns = [
        "total_sessions",
        "total_failures",
        "total_downtime_minutes",
        "avg_queue_minutes",
        "avg_packet_loss_pct",
        "failure_rate_per_100_sessions",
        "latest_avg_queue_minutes",
        "latest_session_count",
        "predicted_failure_probability",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)

    df["queue_component"] = 1 - _min_max_scale(df["latest_avg_queue_minutes"])
    df["reliability_component"] = 1 - (df["failure_rate_per_100_sessions"] / 100).clip(0, 1)
    df["risk_component"] = 1 - df["predicted_failure_probability"].clip(0, 1)
    df["throughput_component"] = _min_max_scale(df["latest_session_count"])
    df["recommendation_score"] = (
        0.40 * df["risk_component"]
        + 0.30 * df["reliability_component"]
        + 0.20 * df["queue_component"]
        + 0.10 * df["throughput_component"]
    ).round(4)

    output_columns = [
        "station_id",
        "source_station_id",
        "station_name",
        "network",
        "city",
        "state",
        "connector_types",
        "port_count",
        "traffic_segment",
        "latest_avg_queue_minutes",
        "latest_session_count",
        "failure_rate_per_100_sessions",
        "predicted_failure_probability",
        "recommendation_score",
    ]
    snapshot = df[output_columns].sort_values(["state", "recommendation_score"], ascending=[True, False])
    output_path = recommender_data_root() / "station_recommendations_snapshot.csv"
    snapshot.to_csv(output_path, index=False)
    return output_path


def recommend_stations(
    state: str,
    top_k: int = 5,
    max_predicted_failure_probability: float = 0.35,
) -> list[dict[str, object]]:
    snapshot_path = recommender_data_root() / "station_recommendations_snapshot.csv"
    if not snapshot_path.exists():
        build_recommendation_snapshot()

    df = pd.read_csv(snapshot_path)
    filtered = df[df["state"].str.upper() == state.upper()].copy()
    if filtered.empty:
        return []

    filtered = filtered[
        filtered["predicted_failure_probability"] <= max_predicted_failure_probability
    ].sort_values("recommendation_score", ascending=False)

    recommendations: list[dict[str, object]] = []
    for row in filtered.head(top_k).to_dict(orient="records"):
        row["explanation"] = (
            f"{row['station_name']} ranks well because it combines lower predicted failure risk, "
            f"lower queue pressure, and stronger recent station performance."
        )
        recommendations.append(row)
    return recommendations


def load_overview_summary() -> dict[str, object]:
    summary = read_json_asset("ml", "exploratory_summary.json")
    top_recommendations = recommend_stations("CA", top_k=3)
    return {
        "project": "ChargeFlow",
        "summary": summary,
        "top_recommendations": top_recommendations,
    }


def _min_max_scale(series: pd.Series) -> pd.Series:
    min_value = series.min()
    max_value = series.max()
    if pd.isna(min_value) or pd.isna(max_value) or min_value == max_value:
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - min_value) / (max_value - min_value)
