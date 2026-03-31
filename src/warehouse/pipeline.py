from __future__ import annotations

import csv
import logging
import sqlite3
from pathlib import Path

from src.utils.config import ROOT_DIR
from src.utils.filesystem import warehouse_data_root, write_csv_records
from src.warehouse.io import (
    latest_raw_energy_rows,
    latest_raw_station_rows,
    latest_raw_weather_rows,
    synthetic_csv_rows,
)
from src.warehouse.quality import run_quality_checks


LOGGER = logging.getLogger(__name__)


def build_warehouse() -> dict[str, Path]:
    db_path = warehouse_data_root() / "chargeflow.db"
    if db_path.exists():
        db_path.unlink()

    connection = sqlite3.connect(db_path)
    try:
        connection.row_factory = sqlite3.Row
        _run_sql_script(connection, ROOT_DIR / "sql" / "warehouse_schema.sql")
        _load_stage_tables(connection)
        _run_sql_script(connection, ROOT_DIR / "sql" / "warehouse_transform_clean.sql")
        _run_sql_script(connection, ROOT_DIR / "sql" / "warehouse_transform_gold.sql")
        dq_results = run_quality_checks(connection)
        mart_exports = _export_gold_tables(connection)
        dq_path = write_csv_records(dq_results, "warehouse", "dq_results.csv")
        LOGGER.info("Warehouse build complete at %s", db_path)
        return {"database": db_path, "dq_results": dq_path, **mart_exports}
    finally:
        connection.close()


def _run_sql_script(connection: sqlite3.Connection, path: Path) -> None:
    with path.open("r", encoding="utf-8") as file:
        connection.executescript(file.read())
    connection.commit()


def _load_stage_tables(connection: sqlite3.Connection) -> None:
    _insert_many(connection, "stage_raw_stations", latest_raw_station_rows())
    _insert_many(connection, "stage_raw_weather_hourly", latest_raw_weather_rows())
    _insert_many(connection, "stage_raw_energy_hourly", latest_raw_energy_rows())
    _insert_many(connection, "stage_augmented_stations", synthetic_csv_rows("augmented_stations.csv"))
    _insert_many(connection, "stage_users", synthetic_csv_rows("users.csv"))
    _insert_many(connection, "stage_vehicles", synthetic_csv_rows("vehicles.csv"))
    _insert_many(connection, "stage_charging_sessions", synthetic_csv_rows("charging_sessions.csv"))
    _insert_many(connection, "stage_telemetry_events", synthetic_csv_rows("telemetry_events.csv"))
    _insert_many(connection, "stage_queue_events", synthetic_csv_rows("queue_events.csv"))
    _insert_many(connection, "stage_failure_events", synthetic_csv_rows("failure_events.csv"))
    _insert_many(connection, "stage_maintenance_tickets", synthetic_csv_rows("maintenance_tickets.csv"))
    _insert_many(connection, "stage_maintenance_notes", synthetic_csv_rows("maintenance_notes.csv"))
    connection.commit()


def _insert_many(connection: sqlite3.Connection, table_name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    values = [tuple(row.get(column) for column in columns) for row in rows]
    connection.executemany(sql, values)


def _export_gold_tables(connection: sqlite3.Connection) -> dict[str, Path]:
    exports: dict[str, Path] = {}
    for table_name in [
        "gold_station_daily_metrics",
        "gold_state_daily_demand",
        "gold_station_health",
        "gold_ml_station_day_features",
    ]:
        rows = _query_table(connection, table_name)
        exports[table_name] = write_csv_records(rows, "warehouse", f"{table_name}.csv")
    return exports


def _query_table(connection: sqlite3.Connection, table_name: str) -> list[dict[str, object]]:
    cursor = connection.execute(f"SELECT * FROM {table_name}")
    return [dict(row) for row in cursor.fetchall()]
