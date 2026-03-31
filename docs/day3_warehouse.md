# Day 3 Warehouse Notes

## Scope

Day 3 loads raw public data and Day 2 synthetic outputs into a local SQL warehouse, transforms them into cleaned dimensions and facts, and publishes gold marts for reporting and machine-learning use cases.

## Warehouse Choice

SQLite is used for Day 3 because it is free, local, requires no extra service, and keeps the warehouse runnable from the Python standard library. The SQL modeling approach is still portable to PostgreSQL later if needed.

## Layers

- `stage_*`: loaded directly from raw JSON and synthetic CSV files
- `dim_*` and `fact_*`: cleaned warehouse layer
- `gold_*`: reporting and ML marts

## Gold Marts

- `gold_station_daily_metrics`: daily station-level utilization and reliability summary
- `gold_state_daily_demand`: daily state-level charging demand with weather and grid context
- `gold_station_health`: station reliability summary across the available history
- `gold_ml_station_day_features`: station-day feature mart for downstream forecasting and failure-risk models

## Run

```bash
python3 -m src.warehouse.cli build-all
```

## Outputs

- `data/processed/warehouse/chargeflow.db`
- `data/processed/warehouse/dq_results.csv`
- `data/processed/warehouse/gold_station_daily_metrics.csv`
- `data/processed/warehouse/gold_state_daily_demand.csv`
- `data/processed/warehouse/gold_station_health.csv`
- `data/processed/warehouse/gold_ml_station_day_features.csv`
