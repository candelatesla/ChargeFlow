from __future__ import annotations

import pandas as pd


def prepare_demand_dataset(demand_df: pd.DataFrame) -> pd.DataFrame:
    df = demand_df.copy()
    df["metric_date"] = pd.to_datetime(df["metric_date"])
    numeric_columns = [
        "session_count",
        "total_energy_kwh",
        "total_revenue_usd",
        "avg_temperature_2m",
        "avg_precipitation_probability",
        "avg_grid_demand_mw",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.sort_values(["state", "metric_date"]).reset_index(drop=True)
    grouped = df.groupby("state", group_keys=False)
    df["lag_session_count"] = grouped["session_count"].shift(1)
    df["lag_total_energy_kwh"] = grouped["total_energy_kwh"].shift(1)
    df["lag_avg_grid_demand_mw"] = grouped["avg_grid_demand_mw"].shift(1)
    df["day_of_week"] = df["metric_date"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    return df.dropna(subset=["lag_session_count", "lag_total_energy_kwh", "lag_avg_grid_demand_mw"])


def prepare_failure_dataset(
    station_day_df: pd.DataFrame,
    station_health_df: pd.DataFrame,
) -> pd.DataFrame:
    df = station_day_df.copy()
    df["metric_date"] = pd.to_datetime(df["metric_date"])

    numeric_columns = [
        "port_count",
        "session_count",
        "total_energy_kwh",
        "avg_queue_minutes",
        "queue_event_count",
        "failure_event_count",
        "avg_temperature_2m",
        "avg_precipitation_probability",
        "avg_grid_demand_mw",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    health_df = station_health_df.copy()
    for column in ["avg_packet_loss_pct", "failure_rate_per_100_sessions", "total_failures"]:
        health_df[column] = pd.to_numeric(health_df[column], errors="coerce")

    df = df.merge(
        health_df[["station_id", "avg_packet_loss_pct", "failure_rate_per_100_sessions", "total_failures"]],
        on="station_id",
        how="left",
    )
    df = df.sort_values(["station_id", "metric_date"]).reset_index(drop=True)
    grouped = df.groupby("station_id", group_keys=False)
    df["lag_session_count"] = grouped["session_count"].shift(1)
    df["lag_total_energy_kwh"] = grouped["total_energy_kwh"].shift(1)
    df["lag_avg_queue_minutes"] = grouped["avg_queue_minutes"].shift(1)
    df["lag_queue_event_count"] = grouped["queue_event_count"].shift(1)
    df["lag_avg_grid_demand_mw"] = grouped["avg_grid_demand_mw"].shift(1)
    df["prior_failure_flag"] = grouped["failure_event_count"].shift(1).fillna(0).gt(0).astype(int)
    df["day_of_week"] = df["metric_date"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["failure_target"] = df["failure_event_count"].gt(0).astype(int)

    return df.dropna(
        subset=[
            "lag_session_count",
            "lag_total_energy_kwh",
            "lag_avg_queue_minutes",
            "lag_queue_event_count",
            "lag_avg_grid_demand_mw",
        ]
    )
