from __future__ import annotations

import logging
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from src.synthetic.loaders import latest_station_file, load_latest_station_records
from src.synthetic.templates import (
    FAILURE_CODES,
    NOTE_TEMPLATES,
    RESOLUTION_CODES,
    TECHNICIAN_NAMES,
    USER_SEGMENTS,
    VEHICLE_CATALOG,
)
from src.utils.config import load_base_config
from src.utils.filesystem import write_csv_records


LOGGER = logging.getLogger(__name__)


def generate_synthetic_data() -> dict[str, Path]:
    config = load_base_config()["synthetic"]
    station_records = load_latest_station_records()
    rng = random.Random(config["seed"])

    augmented_stations = _build_augmented_stations(station_records, rng)
    users = _build_users(augmented_stations, config, rng)
    vehicles = _build_vehicles(users, rng)
    sessions = _build_sessions(augmented_stations, users, vehicles, config, rng)
    telemetry = _build_telemetry(sessions, config, rng)
    queue_events = _build_queue_events(sessions, config, rng)
    failure_events = _build_failure_events(augmented_stations, sessions, config, rng)
    maintenance_tickets = _build_maintenance_tickets(augmented_stations, failure_events, config, rng)
    maintenance_notes = _build_maintenance_notes(maintenance_tickets, failure_events, rng)

    output_paths = {
        "augmented_stations": write_csv_records(augmented_stations, "synthetic", "augmented_stations.csv"),
        "users": write_csv_records(users, "synthetic", "users.csv"),
        "vehicles": write_csv_records(vehicles, "synthetic", "vehicles.csv"),
        "sessions": write_csv_records(sessions, "synthetic", "charging_sessions.csv"),
        "telemetry": write_csv_records(telemetry, "synthetic", "telemetry_events.csv"),
        "queue_events": write_csv_records(queue_events, "synthetic", "queue_events.csv"),
        "failure_events": write_csv_records(failure_events, "synthetic", "failure_events.csv"),
        "maintenance_tickets": write_csv_records(
            maintenance_tickets,
            "synthetic",
            "maintenance_tickets.csv",
        ),
        "maintenance_notes": write_csv_records(
            maintenance_notes,
            "synthetic",
            "maintenance_notes.csv",
        ),
    }

    manifest_path = write_csv_records(
        [
            {
                "source_station_file": str(latest_station_file()),
                "synthetic_seed": config["seed"],
                "station_count": len(augmented_stations),
                "user_count": len(users),
                "vehicle_count": len(vehicles),
                "session_count": len(sessions),
                "telemetry_count": len(telemetry),
                "queue_event_count": len(queue_events),
                "failure_event_count": len(failure_events),
                "ticket_count": len(maintenance_tickets),
                "note_count": len(maintenance_notes),
            }
        ],
        "synthetic",
        "generation_manifest.csv",
    )
    output_paths["manifest"] = manifest_path

    LOGGER.info("Synthetic data generation complete: %s", output_paths)
    return output_paths


def _build_augmented_stations(stations: list[dict[str, Any]], rng: random.Random) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for station in stations:
        source_station_id = station["id"]
        cf_station_id = f"CF-ST-{source_station_id}"
        level2_ports = _coerce_int(station.get("ev_level2_evse_num"))
        dc_fast_ports = _coerce_int(station.get("ev_dc_fast_num"))
        charging_units = _coerce_int(station.get("ev_charging_units")) or max(level2_ports + dc_fast_ports, 1)
        port_total = max(level2_ports + dc_fast_ports, charging_units, 1)
        traffic_score = rng.randint(35, 95)

        records.append(
            {
                "station_id": cf_station_id,
                "source_station_id": source_station_id,
                "station_name": station.get("station_name"),
                "network": station.get("ev_network") or "non_networked",
                "city": station.get("city"),
                "state": station.get("state"),
                "latitude": round(float(station.get("latitude") or 0.0), 6),
                "longitude": round(float(station.get("longitude") or 0.0), 6),
                "access_code": station.get("access_code") or "public",
                "connector_types": "|".join(station.get("ev_connector_types") or ["J1772"]),
                "port_count": port_total,
                "site_power_kw": port_total * rng.choice([7, 11, 19, 50, 150]),
                "traffic_score": traffic_score,
                "traffic_segment": _bucketize(traffic_score, [50, 75], ["low", "medium", "high"]),
                "station_age_years": rng.randint(1, 9),
                "parking_capacity_estimate": port_total + rng.randint(2, 12),
            }
        )
    return records


def _build_users(
    stations: list[dict[str, Any]],
    synthetic_config: dict[str, Any],
    rng: random.Random,
) -> list[dict[str, Any]]:
    states = sorted({station["state"] for station in stations})
    total_users = len(stations) * synthetic_config["users_per_station"]
    users: list[dict[str, Any]] = []

    for index in range(1, total_users + 1):
        segment = rng.choice(USER_SEGMENTS)
        charging_frequency = rng.choice(["daily", "weekday_only", "weekly", "opportunistic"])
        users.append(
            {
                "user_id": f"USR-{index:05d}",
                "home_state": rng.choice(states),
                "driver_segment": segment,
                "charging_frequency": charging_frequency,
                "preferred_arrival_window": rng.choice(["morning", "midday", "evening", "late_night"]),
                "range_anxiety_score": rng.randint(20, 95),
                "price_sensitivity_score": rng.randint(15, 90),
                "reliability_sensitivity_score": rng.randint(35, 98),
            }
        )
    return users


def _build_vehicles(users: list[dict[str, Any]], rng: random.Random) -> list[dict[str, Any]]:
    vehicles: list[dict[str, Any]] = []
    for index, user in enumerate(users, start=1):
        template = rng.choice(VEHICLE_CATALOG)
        vehicles.append(
            {
                "vehicle_id": f"VEH-{index:05d}",
                "user_id": user["user_id"],
                "make": template["make"],
                "model": template["model"],
                "connector_type": template["connector"],
                "battery_kwh": template["battery_kwh"],
                "efficiency_wh_per_mile": rng.randint(240, 390),
                "max_charge_power_kw": rng.choice([7.2, 11.5, 50.0, 150.0]),
                "home_state": user["home_state"],
            }
        )
    return vehicles


def _build_sessions(
    stations: list[dict[str, Any]],
    users: list[dict[str, Any]],
    vehicles: list[dict[str, Any]],
    synthetic_config: dict[str, Any],
    rng: random.Random,
) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    lookback_days = synthetic_config["lookback_days"]
    vehicles_by_user = {vehicle["user_id"]: vehicle for vehicle in vehicles}
    user_pool = users[:]
    sessions: list[dict[str, Any]] = []
    session_counter = 1

    for station in stations:
        session_count = rng.randint(
            synthetic_config["sessions_per_station_min"],
            synthetic_config["sessions_per_station_max"],
        )
        for _ in range(session_count):
            user = rng.choice(user_pool)
            vehicle = vehicles_by_user[user["user_id"]]
            connector_type = vehicle["connector_type"]
            start_at = now - timedelta(
                days=rng.randint(0, lookback_days),
                hours=rng.randint(0, 23),
                minutes=rng.randint(0, 59),
            )
            duration_minutes = rng.randint(18, 140)
            end_at = start_at + timedelta(minutes=duration_minutes)
            energy_kwh = round(duration_minutes * rng.uniform(0.35, 0.95), 2)
            queue_minutes = rng.randint(0, 35) if rng.random() < 0.45 else 0
            peak_period = start_at.hour in {7, 8, 9, 16, 17, 18, 19}

            sessions.append(
                {
                    "session_id": f"SES-{session_counter:06d}",
                    "station_id": station["station_id"],
                    "source_station_id": station["source_station_id"],
                    "user_id": user["user_id"],
                    "vehicle_id": vehicle["vehicle_id"],
                    "connector_type": connector_type,
                    "port_number": rng.randint(1, max(int(station["port_count"]), 1)),
                    "session_start_utc": start_at.isoformat(),
                    "session_end_utc": end_at.isoformat(),
                    "session_duration_minutes": duration_minutes,
                    "energy_kwh": energy_kwh,
                    "queue_minutes": queue_minutes,
                    "peak_period_flag": str(peak_period).lower(),
                    "price_usd": round(energy_kwh * rng.uniform(0.18, 0.48), 2),
                    "start_soc_pct": rng.randint(8, 58),
                    "end_soc_pct": rng.randint(62, 96),
                    "weather_impact_label": rng.choice(["normal", "hot_day", "rainy", "windy"]),
                    "driver_segment": user["driver_segment"],
                }
            )
            session_counter += 1
    return sessions


def _build_telemetry(
    sessions: list[dict[str, Any]],
    synthetic_config: dict[str, Any],
    rng: random.Random,
) -> list[dict[str, Any]]:
    telemetry: list[dict[str, Any]] = []
    counter = 1
    for session in sessions:
        event_count = rng.randint(
            synthetic_config["telemetry_events_per_session_min"],
            synthetic_config["telemetry_events_per_session_max"],
        )
        session_start = datetime.fromisoformat(session["session_start_utc"])
        for sequence in range(event_count):
            event_ts = session_start + timedelta(minutes=sequence * max(session["session_duration_minutes"] // event_count, 1))
            telemetry.append(
                {
                    "telemetry_id": f"TEL-{counter:07d}",
                    "station_id": session["station_id"],
                    "session_id": session["session_id"],
                    "port_number": session["port_number"],
                    "event_ts_utc": event_ts.isoformat(),
                    "heartbeat_status": rng.choice(["online", "online", "online", "degraded"]),
                    "power_kw": round(rng.uniform(6.0, 145.0), 2),
                    "voltage": round(rng.uniform(380.0, 495.0), 1),
                    "current_amps": round(rng.uniform(18.0, 240.0), 1),
                    "connector_temperature_c": round(rng.uniform(24.0, 66.0), 1),
                    "packet_loss_pct": round(rng.uniform(0.0, 3.4), 2),
                }
            )
            counter += 1
    return telemetry


def _build_queue_events(
    sessions: list[dict[str, Any]],
    synthetic_config: dict[str, Any],
    rng: random.Random,
) -> list[dict[str, Any]]:
    queue_events: list[dict[str, Any]] = []
    counter = 1
    for session in sessions:
        if session["queue_minutes"] == 0 or rng.random() > synthetic_config["queue_event_probability"]:
            continue
        queue_events.append(
            {
                "queue_event_id": f"QUE-{counter:06d}",
                "station_id": session["station_id"],
                "session_id": session["session_id"],
                "event_ts_utc": session["session_start_utc"],
                "queue_depth": rng.randint(1, 5),
                "estimated_wait_minutes": session["queue_minutes"],
                "queue_reason": rng.choice(["high_demand_peak", "single_port_available", "slow_turnover"]),
            }
        )
        counter += 1
    return queue_events


def _build_failure_events(
    stations: list[dict[str, Any]],
    sessions: list[dict[str, Any]],
    synthetic_config: dict[str, Any],
    rng: random.Random,
) -> list[dict[str, Any]]:
    sessions_by_station: dict[str, list[dict[str, Any]]] = {}
    for session in sessions:
        sessions_by_station.setdefault(session["station_id"], []).append(session)

    failure_events: list[dict[str, Any]] = []
    counter = 1
    for station in stations:
        if rng.random() > synthetic_config["failure_event_probability"]:
            continue

        station_sessions = sessions_by_station.get(station["station_id"], [])
        related_session = rng.choice(station_sessions) if station_sessions else None
        failure_code, symptom = rng.choice(FAILURE_CODES)
        opened_at = (
            datetime.fromisoformat(related_session["session_start_utc"])
            if related_session
            else datetime.now(timezone.utc) - timedelta(days=rng.randint(1, synthetic_config["lookback_days"]))
        )
        resolved_at = opened_at + timedelta(minutes=rng.randint(22, 420))

        failure_events.append(
            {
                "failure_event_id": f"FLR-{counter:05d}",
                "station_id": station["station_id"],
                "source_station_id": station["source_station_id"],
                "session_id": related_session["session_id"] if related_session else "",
                "port_number": related_session["port_number"] if related_session else rng.randint(1, max(int(station["port_count"]), 1)),
                "opened_at_utc": opened_at.isoformat(),
                "resolved_at_utc": resolved_at.isoformat(),
                "downtime_minutes": int((resolved_at - opened_at).total_seconds() // 60),
                "severity": rng.choice(["low", "medium", "high"]),
                "failure_code": failure_code,
                "symptom_summary": symptom,
            }
        )
        counter += 1
    return failure_events


def _build_maintenance_tickets(
    stations: list[dict[str, Any]],
    failure_events: list[dict[str, Any]],
    synthetic_config: dict[str, Any],
    rng: random.Random,
) -> list[dict[str, Any]]:
    tickets: list[dict[str, Any]] = []
    counter = 1

    for failure_event in failure_events:
        opened_at = datetime.fromisoformat(failure_event["opened_at_utc"])
        closed_at = datetime.fromisoformat(failure_event["resolved_at_utc"]) + timedelta(minutes=rng.randint(10, 180))
        resolution_code = rng.choice(RESOLUTION_CODES)
        tickets.append(
            {
                "ticket_id": f"TIC-{counter:05d}",
                "station_id": failure_event["station_id"],
                "failure_event_id": failure_event["failure_event_id"],
                "ticket_type": "corrective",
                "priority": failure_event["severity"],
                "status": "closed",
                "opened_at_utc": opened_at.isoformat(),
                "closed_at_utc": closed_at.isoformat(),
                "technician_name": rng.choice(TECHNICIAN_NAMES),
                "resolution_code": resolution_code,
                "summary": f"Resolved {failure_event['failure_code']} on port {failure_event['port_number']}.",
            }
        )
        counter += 1

    for station in stations:
        if rng.random() > synthetic_config["preventive_ticket_probability"]:
            continue
        opened_at = datetime.now(timezone.utc) - timedelta(days=rng.randint(1, synthetic_config["lookback_days"]))
        closed_at = opened_at + timedelta(minutes=rng.randint(30, 150))
        resolution_code = rng.choice(RESOLUTION_CODES)
        tickets.append(
            {
                "ticket_id": f"TIC-{counter:05d}",
                "station_id": station["station_id"],
                "failure_event_id": "",
                "ticket_type": "preventive",
                "priority": "low",
                "status": "closed",
                "opened_at_utc": opened_at.isoformat(),
                "closed_at_utc": closed_at.isoformat(),
                "technician_name": rng.choice(TECHNICIAN_NAMES),
                "resolution_code": resolution_code,
                "summary": "Preventive maintenance inspection completed during low-traffic window.",
            }
        )
        counter += 1
    return tickets


def _build_maintenance_notes(
    tickets: list[dict[str, Any]],
    failure_events: list[dict[str, Any]],
    rng: random.Random,
) -> list[dict[str, Any]]:
    failure_lookup = {event["failure_event_id"]: event for event in failure_events}
    notes: list[dict[str, Any]] = []
    counter = 1
    for ticket in tickets:
        failure = failure_lookup.get(ticket["failure_event_id"], {})
        for sequence, template in enumerate(NOTE_TEMPLATES, start=1):
            note_timestamp = datetime.fromisoformat(ticket["opened_at_utc"]) + timedelta(minutes=sequence * 12)
            note_text = template.format(
                failure_code=failure.get("failure_code", "preventive_check"),
                symptom=failure.get("symptom_summary", "routine inspection findings"),
                port_number=failure.get("port_number", 1),
                resolution_code=ticket["resolution_code"],
            )
            notes.append(
                {
                    "note_id": f"NOT-{counter:06d}",
                    "ticket_id": ticket["ticket_id"],
                    "station_id": ticket["station_id"],
                    "note_ts_utc": note_timestamp.isoformat(),
                    "author_role": rng.choice(["field_technician", "operations_manager"]),
                    "sop_reference": rng.choice(["SOP-CHG-12", "SOP-NET-04", "SOP-SAFE-09"]),
                    "parts_used": rng.choice(["none", "connector_cable", "breaker_module", "card_reader"]),
                    "note_text": note_text,
                }
            )
            counter += 1
    return notes


def _bucketize(value: int, cutoffs: list[int], labels: list[str]) -> str:
    if value < cutoffs[0]:
        return labels[0]
    if value < cutoffs[1]:
        return labels[1]
    return labels[2]


def _coerce_int(value: Any) -> int:
    if value in (None, "", []):
        return 0
    if isinstance(value, list):
        return len(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
