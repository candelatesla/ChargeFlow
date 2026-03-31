import csv
import sqlite3
import unittest
from pathlib import Path

from src.warehouse.pipeline import build_warehouse


class WarehousePipelineTests(unittest.TestCase):
    def test_build_warehouse_creates_database_and_gold_outputs(self) -> None:
        outputs = build_warehouse()

        self.assertTrue(outputs["database"].exists())
        self.assertTrue(outputs["dq_results"].exists())
        self.assertTrue(outputs["gold_station_daily_metrics"].exists())
        self.assertTrue(outputs["gold_state_daily_demand"].exists())
        self.assertTrue(outputs["gold_station_health"].exists())
        self.assertTrue(outputs["gold_ml_station_day_features"].exists())

        with sqlite3.connect(outputs["database"]) as connection:
            station_count = connection.execute("SELECT COUNT(*) FROM dim_station").fetchone()[0]
            session_count = connection.execute("SELECT COUNT(*) FROM fact_charging_sessions").fetchone()[0]
            gold_count = connection.execute("SELECT COUNT(*) FROM gold_station_daily_metrics").fetchone()[0]

        self.assertGreater(station_count, 0)
        self.assertGreater(session_count, 0)
        self.assertGreater(gold_count, 0)

        with outputs["dq_results"].open("r", encoding="utf-8", newline="") as file:
            rows = list(csv.DictReader(file))
        self.assertTrue(rows)


if __name__ == "__main__":
    unittest.main()
