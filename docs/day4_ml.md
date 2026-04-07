# Day 4 Analytics and ML Notes

## Scope

Day 4 trains baseline models on the Day 3 gold marts and saves reproducible artifacts, metrics, and prediction outputs.

## Models

- Demand forecasting baseline:
  - Grain: state-day
  - Target: `session_count`
  - Model: Random forest regressor

- Failure-risk baseline:
  - Grain: station-day
  - Target: whether `failure_event_count > 0`
  - Model: Logistic regression with balanced class weights

## Outputs

- `data/processed/ml/exploratory_summary.json`
- `data/processed/ml/model_features.md`
- `data/processed/ml/demand_forecast_model.joblib`
- `data/processed/ml/demand_forecast_metrics.json`
- `data/processed/ml/demand_forecast_predictions.csv`
- `data/processed/ml/failure_risk_model.joblib`
- `data/processed/ml/failure_risk_metrics.json`
- `data/processed/ml/failure_risk_predictions.csv`

## Run

```bash
python3 -m src.ml.cli run-all
```
