from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_exploratory_summary(
    demand_df: pd.DataFrame,
    failure_df: pd.DataFrame,
) -> dict[str, object]:
    date_range = {
        "demand_min_date": demand_df["metric_date"].min().strftime("%Y-%m-%d"),
        "demand_max_date": demand_df["metric_date"].max().strftime("%Y-%m-%d"),
        "failure_min_date": failure_df["metric_date"].min().strftime("%Y-%m-%d"),
        "failure_max_date": failure_df["metric_date"].max().strftime("%Y-%m-%d"),
    }

    return {
        "row_counts": {
            "demand_rows": int(len(demand_df)),
            "failure_rows": int(len(failure_df)),
            "states": int(demand_df["state"].nunique()),
            "stations": int(failure_df["station_id"].nunique()),
        },
        "date_range": date_range,
        "demand_summary": {
            "avg_daily_sessions": round(float(demand_df["session_count"].mean()), 2),
            "avg_daily_energy_kwh": round(float(demand_df["total_energy_kwh"].mean()), 2),
            "avg_grid_demand_mw": round(float(demand_df["avg_grid_demand_mw"].dropna().mean()), 2),
        },
        "failure_summary": {
            "positive_failure_days": int(failure_df["failure_target"].sum()),
            "failure_rate_pct": round(float(failure_df["failure_target"].mean() * 100), 2),
            "avg_queue_minutes": round(float(failure_df["avg_queue_minutes"].mean()), 2),
        },
    }


def build_feature_documentation() -> str:
    return """# Day 4 Model Features and Targets

## Demand Forecasting Baseline

- Grain: state-day
- Target: `session_count`
- Features:
  - `state`
  - `day_of_week`
  - `is_weekend`
  - `lag_session_count`
  - `lag_total_energy_kwh`
  - `lag_avg_grid_demand_mw`
  - `avg_temperature_2m`
  - `avg_precipitation_probability`

## Failure-Risk Baseline

- Grain: station-day
- Target: `failure_target` where `failure_event_count > 0`
- Features:
  - `state`
  - `traffic_segment`
  - `port_count`
  - `day_of_week`
  - `is_weekend`
  - `lag_session_count`
  - `lag_total_energy_kwh`
  - `lag_avg_queue_minutes`
  - `lag_queue_event_count`
  - `lag_avg_grid_demand_mw`
  - `avg_temperature_2m`
  - `avg_precipitation_probability`
  - `avg_packet_loss_pct`
  - `failure_rate_per_100_sessions`
  - `prior_failure_flag`
"""
