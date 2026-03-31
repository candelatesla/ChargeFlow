from __future__ import annotations

import sqlite3


QUALITY_CHECKS = [
    (
        "dim_station_nonzero",
        "warehouse",
        "SELECT CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END AS failed_rows FROM dim_station",
        "dim_station should contain at least one record.",
    ),
    (
        "orphan_sessions_station",
        "warehouse",
        """
        SELECT COUNT(*) AS failed_rows
        FROM fact_charging_sessions s
        LEFT JOIN dim_station d ON s.station_id = d.station_id
        WHERE d.station_id IS NULL
        """,
        "Every session should map to a station.",
    ),
    (
        "orphan_sessions_vehicle",
        "warehouse",
        """
        SELECT COUNT(*) AS failed_rows
        FROM fact_charging_sessions s
        LEFT JOIN dim_vehicle v ON s.vehicle_id = v.vehicle_id
        WHERE v.vehicle_id IS NULL
        """,
        "Every session should map to a vehicle.",
    ),
    (
        "invalid_session_timestamps",
        "warehouse",
        """
        SELECT COUNT(*) AS failed_rows
        FROM fact_charging_sessions
        WHERE session_end_utc <= session_start_utc
        """,
        "Session end time must be after session start time.",
    ),
    (
        "negative_energy_sessions",
        "warehouse",
        """
        SELECT COUNT(*) AS failed_rows
        FROM fact_charging_sessions
        WHERE energy_kwh < 0
        """,
        "Session energy cannot be negative.",
    ),
    (
        "orphan_maintenance_notes",
        "warehouse",
        """
        SELECT COUNT(*) AS failed_rows
        FROM fact_maintenance_notes n
        LEFT JOIN fact_maintenance_tickets t ON n.ticket_id = t.ticket_id
        WHERE t.ticket_id IS NULL
        """,
        "Every maintenance note should map to a ticket.",
    ),
    (
        "gold_station_daily_metrics_nonzero",
        "gold",
        "SELECT CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END AS failed_rows FROM gold_station_daily_metrics",
        "gold_station_daily_metrics should contain records.",
    ),
]


def run_quality_checks(connection: sqlite3.Connection) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    connection.execute("DELETE FROM dq_results")
    for check_name, check_level, sql, detail in QUALITY_CHECKS:
        cursor = connection.execute(sql)
        row = cursor.fetchone()
        failed_rows = 0
        if row is None:
            failed_rows = 1
        else:
            failed_rows = int(row[0] or 0)

        status = "PASS" if failed_rows == 0 else "FAIL"
        result = {
            "check_name": check_name,
            "check_level": check_level,
            "status": status,
            "failed_rows": failed_rows,
            "detail": detail,
        }
        results.append(result)
        connection.execute(
            """
            INSERT INTO dq_results (check_name, check_level, status, failed_rows, detail)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                result["check_name"],
                result["check_level"],
                result["status"],
                result["failed_rows"],
                result["detail"],
            ),
        )
    connection.commit()
    return results
