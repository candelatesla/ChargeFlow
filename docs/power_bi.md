# Power BI Guide

## Option 1: Use Exported CSV Files

Generate the Power BI bundle:

```bash
python3 scripts/export_powerbi.py
```

This creates files in:

- `data/gold/power_bi_exports/`

Recommended tables to load into Power BI:

- `powerbi_gold_station_daily_metrics.csv`
- `powerbi_gold_state_daily_demand.csv`
- `powerbi_gold_station_health.csv`
- `powerbi_gold_ml_station_day_features.csv`
- `powerbi_failure_risk_predictions.csv`
- `powerbi_station_recommendations_snapshot.csv`

## Option 2: Connect Directly to SQLite

If you prefer a direct model-driven connection, use the SQLite warehouse:

- file: `data/processed/warehouse/chargeflow.db`

Suggested Power BI tables:

- `gold_station_daily_metrics`
- `gold_state_daily_demand`
- `gold_station_health`
- `gold_ml_station_day_features`

## Recommended Demo Story

- Start with `gold_state_daily_demand` for demand trends by state
- Use `gold_station_health` for station-level reliability
- Add `powerbi_failure_risk_predictions.csv` as a model output layer
- Add `powerbi_station_recommendations_snapshot.csv` to show decision support
