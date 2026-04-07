from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.ml.analytics import build_exploratory_summary, build_feature_documentation
from src.ml.features import prepare_demand_dataset, prepare_failure_dataset
from src.utils.config import load_base_config
from src.utils.filesystem import ml_data_root


LOGGER = logging.getLogger(__name__)


def run_ml_pipeline() -> dict[str, Path]:
    ml_root = ml_data_root()
    config = load_base_config()["ml"]
    demand_source = pd.read_csv("data/processed/warehouse/gold_state_daily_demand.csv")
    station_day_source = pd.read_csv("data/processed/warehouse/gold_ml_station_day_features.csv")
    station_health_source = pd.read_csv("data/processed/warehouse/gold_station_health.csv")

    demand_df = prepare_demand_dataset(demand_source)
    failure_df = prepare_failure_dataset(station_day_source, station_health_source)

    exploratory_summary = build_exploratory_summary(demand_df, failure_df)
    exploratory_path = ml_root / "exploratory_summary.json"
    exploratory_path.write_text(json.dumps(exploratory_summary, indent=2), encoding="utf-8")

    feature_doc_path = ml_root / "model_features.md"
    feature_doc_path.write_text(build_feature_documentation(), encoding="utf-8")

    demand_outputs = _train_demand_model(demand_df, config, ml_root)
    failure_outputs = _train_failure_model(failure_df, config, ml_root)

    outputs = {
        "exploratory_summary": exploratory_path,
        "feature_documentation": feature_doc_path,
        **demand_outputs,
        **failure_outputs,
    }
    LOGGER.info("ML pipeline complete: %s", outputs)
    return outputs


def _train_demand_model(
    df: pd.DataFrame,
    config: dict[str, int],
    ml_root: Path,
) -> dict[str, Path]:
    candidate_features = [
        "state",
        "day_of_week",
        "is_weekend",
        "lag_session_count",
        "lag_total_energy_kwh",
        "lag_avg_grid_demand_mw",
        "avg_temperature_2m",
        "avg_precipitation_probability",
    ]
    target = "session_count"

    train_df, test_df = _time_holdout_split(df, "metric_date", config["demand_holdout_days"])
    features = _usable_features(train_df, candidate_features)
    categorical_features = [feature for feature in ["state"] if feature in features]
    numeric_features = [feature for feature in features if feature not in categorical_features]
    preprocessor = _build_preprocessor(categorical_features=categorical_features, numeric_features=numeric_features)
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=250,
                    max_depth=8,
                    min_samples_leaf=2,
                    random_state=config["random_seed"],
                ),
            ),
        ]
    )
    model.fit(train_df[features], train_df[target])
    predictions = model.predict(test_df[features])

    metrics = {
        "mae": round(float(mean_absolute_error(test_df[target], predictions)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(test_df[target], predictions))), 4),
        "r2": round(float(r2_score(test_df[target], predictions)), 4),
    }

    predictions_df = test_df[["state", "metric_date", target]].copy()
    predictions_df["predicted_session_count"] = np.round(predictions, 2)
    predictions_path = ml_root / "demand_forecast_predictions.csv"
    predictions_df.to_csv(predictions_path, index=False)

    metrics_path = ml_root / "demand_forecast_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    artifact_path = ml_root / "demand_forecast_model.joblib"
    joblib.dump({"model": model, "features": features, "target": target}, artifact_path)

    return {
        "demand_model": artifact_path,
        "demand_metrics": metrics_path,
        "demand_predictions": predictions_path,
    }


def _train_failure_model(
    df: pd.DataFrame,
    config: dict[str, int],
    ml_root: Path,
) -> dict[str, Path]:
    candidate_features = [
        "state",
        "traffic_segment",
        "port_count",
        "day_of_week",
        "is_weekend",
        "lag_session_count",
        "lag_total_energy_kwh",
        "lag_avg_queue_minutes",
        "lag_queue_event_count",
        "lag_avg_grid_demand_mw",
        "avg_temperature_2m",
        "avg_precipitation_probability",
        "avg_packet_loss_pct",
        "failure_rate_per_100_sessions",
        "prior_failure_flag",
    ]
    target = "failure_target"

    train_df, test_df = _failure_split(df, config["failure_holdout_days"])
    features = _usable_features(train_df, candidate_features)
    categorical_features = [feature for feature in ["state", "traffic_segment"] if feature in features]
    numeric_features = [feature for feature in features if feature not in categorical_features]
    preprocessor = _build_preprocessor(
        categorical_features=categorical_features,
        numeric_features=numeric_features,
    )
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=config["random_seed"],
                    solver="liblinear",
                ),
            ),
        ]
    )
    model.fit(train_df[features], train_df[target])
    probabilities = model.predict_proba(test_df[features])[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    metrics = {
        "accuracy": round(float(accuracy_score(test_df[target], predictions)), 4),
        "precision": round(float(precision_score(test_df[target], predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(test_df[target], predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(test_df[target], predictions, zero_division=0)), 4),
        "roc_auc": round(float(_safe_roc_auc(test_df[target], probabilities)), 4),
        "positive_rate_test": round(float(test_df[target].mean()), 4),
    }

    predictions_df = test_df[["station_id", "metric_date", target]].copy()
    predictions_df["predicted_failure_probability"] = np.round(probabilities, 4)
    predictions_df["predicted_failure_flag"] = predictions
    predictions_path = ml_root / "failure_risk_predictions.csv"
    predictions_df.to_csv(predictions_path, index=False)

    metrics_path = ml_root / "failure_risk_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    artifact_path = ml_root / "failure_risk_model.joblib"
    joblib.dump({"model": model, "features": features, "target": target}, artifact_path)

    return {
        "failure_model": artifact_path,
        "failure_metrics": metrics_path,
        "failure_predictions": predictions_path,
    }


def _build_preprocessor(categorical_features: list[str], numeric_features: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                    ]
                ),
                numeric_features,
            ),
        ]
    )


def _time_holdout_split(df: pd.DataFrame, date_column: str, holdout_days: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    ordered_dates = sorted(df[date_column].dt.normalize().unique())
    cutoff_dates = ordered_dates[-holdout_days:]
    test_df = df[df[date_column].dt.normalize().isin(cutoff_dates)].copy()
    train_df = df[~df[date_column].dt.normalize().isin(cutoff_dates)].copy()
    return train_df, test_df


def _failure_split(df: pd.DataFrame, holdout_days: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_df, test_df = _time_holdout_split(df, "metric_date", holdout_days)
    if test_df["failure_target"].nunique() > 1 and train_df["failure_target"].sum() > 0:
        return train_df, test_df

    rng = np.random.RandomState(42)
    sampled_index = rng.permutation(df.index.to_numpy())
    split_point = int(len(sampled_index) * 0.8)
    train_idx = sampled_index[:split_point]
    test_idx = sampled_index[split_point:]
    return df.loc[train_idx].copy(), df.loc[test_idx].copy()


def _safe_roc_auc(y_true: pd.Series, y_score: np.ndarray) -> float:
    if y_true.nunique() < 2:
        return 0.0
    return float(roc_auc_score(y_true, y_score))


def _usable_features(train_df: pd.DataFrame, candidate_features: list[str]) -> list[str]:
    usable: list[str] = []
    for feature in candidate_features:
        if feature not in train_df.columns:
            continue
        if train_df[feature].notna().any():
            usable.append(feature)
    return usable
