from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.recommender.service import build_recommendation_snapshot
from src.utils.assets import asset_csv_path
from src.utils.filesystem import gold_data_root


EXPORTS = {
    "powerbi_gold_station_daily_metrics.csv": ("warehouse", "gold_station_daily_metrics.csv"),
    "powerbi_gold_state_daily_demand.csv": ("warehouse", "gold_state_daily_demand.csv"),
    "powerbi_gold_station_health.csv": ("warehouse", "gold_station_health.csv"),
    "powerbi_gold_ml_station_day_features.csv": ("warehouse", "gold_ml_station_day_features.csv"),
    "powerbi_failure_risk_predictions.csv": ("ml", "failure_risk_predictions.csv"),
    "powerbi_station_recommendations_snapshot.csv": ("recommender", "station_recommendations_snapshot.csv"),
}


def export_powerbi_bundle() -> list[Path]:
    build_recommendation_snapshot()
    output_dir = gold_data_root() / "power_bi_exports"
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs: list[Path] = []
    for export_name, (category, source_name) in EXPORTS.items():
        source_path = asset_csv_path(category, source_name)
        target_path = output_dir / export_name
        shutil.copyfile(source_path, target_path)
        outputs.append(target_path)
    return outputs


if __name__ == "__main__":
    for path in export_powerbi_bundle():
        print(path)
