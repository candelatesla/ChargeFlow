DROP TABLE IF EXISTS stage_raw_stations;
DROP TABLE IF EXISTS stage_raw_weather_hourly;
DROP TABLE IF EXISTS stage_raw_energy_hourly;
DROP TABLE IF EXISTS stage_augmented_stations;
DROP TABLE IF EXISTS stage_users;
DROP TABLE IF EXISTS stage_vehicles;
DROP TABLE IF EXISTS stage_charging_sessions;
DROP TABLE IF EXISTS stage_telemetry_events;
DROP TABLE IF EXISTS stage_queue_events;
DROP TABLE IF EXISTS stage_failure_events;
DROP TABLE IF EXISTS stage_maintenance_tickets;
DROP TABLE IF EXISTS stage_maintenance_notes;
DROP TABLE IF EXISTS dq_results;
DROP TABLE IF EXISTS dim_station;
DROP TABLE IF EXISTS dim_user;
DROP TABLE IF EXISTS dim_vehicle;
DROP TABLE IF EXISTS fact_charging_sessions;
DROP TABLE IF EXISTS fact_telemetry_events;
DROP TABLE IF EXISTS fact_queue_events;
DROP TABLE IF EXISTS fact_failure_events;
DROP TABLE IF EXISTS fact_maintenance_tickets;
DROP TABLE IF EXISTS fact_maintenance_notes;
DROP TABLE IF EXISTS fact_weather_hourly;
DROP TABLE IF EXISTS fact_energy_hourly;
DROP TABLE IF EXISTS gold_station_daily_metrics;
DROP TABLE IF EXISTS gold_state_daily_demand;
DROP TABLE IF EXISTS gold_station_health;
DROP TABLE IF EXISTS gold_ml_station_day_features;

CREATE TABLE stage_raw_stations (
    source_station_id TEXT,
    station_name TEXT,
    city TEXT,
    state TEXT,
    access_code TEXT,
    ev_network TEXT,
    ev_connector_types TEXT,
    latitude REAL,
    longitude REAL,
    ev_level2_evse_num INTEGER,
    ev_dc_fast_num INTEGER,
    ev_charging_units INTEGER
);

CREATE TABLE stage_raw_weather_hourly (
    weather_row_id INTEGER PRIMARY KEY,
    station_group TEXT,
    state TEXT,
    observation_ts_utc TEXT,
    temperature_2m REAL,
    apparent_temperature REAL,
    precipitation_probability REAL,
    cloud_cover REAL,
    wind_speed_10m REAL
);

CREATE TABLE stage_raw_energy_hourly (
    energy_row_id INTEGER PRIMARY KEY,
    respondent TEXT,
    state TEXT,
    period_utc TEXT,
    value REAL,
    value_type TEXT
);

CREATE TABLE stage_augmented_stations (
    station_id TEXT,
    source_station_id TEXT,
    station_name TEXT,
    network TEXT,
    city TEXT,
    state TEXT,
    latitude REAL,
    longitude REAL,
    access_code TEXT,
    connector_types TEXT,
    port_count INTEGER,
    site_power_kw REAL,
    traffic_score INTEGER,
    traffic_segment TEXT,
    station_age_years INTEGER,
    parking_capacity_estimate INTEGER
);

CREATE TABLE stage_users (
    user_id TEXT,
    home_state TEXT,
    driver_segment TEXT,
    charging_frequency TEXT,
    preferred_arrival_window TEXT,
    range_anxiety_score INTEGER,
    price_sensitivity_score INTEGER,
    reliability_sensitivity_score INTEGER
);

CREATE TABLE stage_vehicles (
    vehicle_id TEXT,
    user_id TEXT,
    make TEXT,
    model TEXT,
    connector_type TEXT,
    battery_kwh REAL,
    efficiency_wh_per_mile REAL,
    max_charge_power_kw REAL,
    home_state TEXT
);

CREATE TABLE stage_charging_sessions (
    session_id TEXT,
    station_id TEXT,
    source_station_id TEXT,
    user_id TEXT,
    vehicle_id TEXT,
    connector_type TEXT,
    port_number INTEGER,
    session_start_utc TEXT,
    session_end_utc TEXT,
    session_duration_minutes INTEGER,
    energy_kwh REAL,
    queue_minutes INTEGER,
    peak_period_flag TEXT,
    price_usd REAL,
    start_soc_pct INTEGER,
    end_soc_pct INTEGER,
    weather_impact_label TEXT,
    driver_segment TEXT
);

CREATE TABLE stage_telemetry_events (
    telemetry_id TEXT,
    station_id TEXT,
    session_id TEXT,
    port_number INTEGER,
    event_ts_utc TEXT,
    heartbeat_status TEXT,
    power_kw REAL,
    voltage REAL,
    current_amps REAL,
    connector_temperature_c REAL,
    packet_loss_pct REAL
);

CREATE TABLE stage_queue_events (
    queue_event_id TEXT,
    station_id TEXT,
    session_id TEXT,
    event_ts_utc TEXT,
    queue_depth INTEGER,
    estimated_wait_minutes INTEGER,
    queue_reason TEXT
);

CREATE TABLE stage_failure_events (
    failure_event_id TEXT,
    station_id TEXT,
    source_station_id TEXT,
    session_id TEXT,
    port_number INTEGER,
    opened_at_utc TEXT,
    resolved_at_utc TEXT,
    downtime_minutes INTEGER,
    severity TEXT,
    failure_code TEXT,
    symptom_summary TEXT
);

CREATE TABLE stage_maintenance_tickets (
    ticket_id TEXT,
    station_id TEXT,
    failure_event_id TEXT,
    ticket_type TEXT,
    priority TEXT,
    status TEXT,
    opened_at_utc TEXT,
    closed_at_utc TEXT,
    technician_name TEXT,
    resolution_code TEXT,
    summary TEXT
);

CREATE TABLE stage_maintenance_notes (
    note_id TEXT,
    ticket_id TEXT,
    station_id TEXT,
    note_ts_utc TEXT,
    author_role TEXT,
    sop_reference TEXT,
    parts_used TEXT,
    note_text TEXT
);

CREATE TABLE dq_results (
    check_name TEXT,
    check_level TEXT,
    status TEXT,
    failed_rows INTEGER,
    detail TEXT
);

CREATE TABLE dim_station (
    station_key INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id TEXT UNIQUE,
    source_station_id TEXT,
    station_name TEXT,
    network TEXT,
    city TEXT,
    state TEXT,
    access_code TEXT,
    connector_types TEXT,
    port_count INTEGER,
    site_power_kw REAL,
    traffic_segment TEXT,
    traffic_score INTEGER,
    station_age_years INTEGER
);

CREATE TABLE dim_user (
    user_key INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE,
    home_state TEXT,
    driver_segment TEXT,
    charging_frequency TEXT,
    preferred_arrival_window TEXT,
    range_anxiety_score INTEGER,
    price_sensitivity_score INTEGER,
    reliability_sensitivity_score INTEGER
);

CREATE TABLE dim_vehicle (
    vehicle_key INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT UNIQUE,
    user_id TEXT,
    make TEXT,
    model TEXT,
    connector_type TEXT,
    battery_kwh REAL,
    efficiency_wh_per_mile REAL,
    max_charge_power_kw REAL,
    home_state TEXT
);

CREATE TABLE fact_charging_sessions (
    session_id TEXT PRIMARY KEY,
    station_id TEXT,
    user_id TEXT,
    vehicle_id TEXT,
    session_date TEXT,
    session_start_utc TEXT,
    session_end_utc TEXT,
    session_duration_minutes INTEGER,
    energy_kwh REAL,
    queue_minutes INTEGER,
    peak_period_flag INTEGER,
    price_usd REAL,
    start_soc_pct INTEGER,
    end_soc_pct INTEGER,
    weather_impact_label TEXT
);

CREATE TABLE fact_telemetry_events (
    telemetry_id TEXT PRIMARY KEY,
    station_id TEXT,
    session_id TEXT,
    event_ts_utc TEXT,
    heartbeat_status TEXT,
    power_kw REAL,
    voltage REAL,
    current_amps REAL,
    connector_temperature_c REAL,
    packet_loss_pct REAL
);

CREATE TABLE fact_queue_events (
    queue_event_id TEXT PRIMARY KEY,
    station_id TEXT,
    session_id TEXT,
    queue_date TEXT,
    event_ts_utc TEXT,
    queue_depth INTEGER,
    estimated_wait_minutes INTEGER,
    queue_reason TEXT
);

CREATE TABLE fact_failure_events (
    failure_event_id TEXT PRIMARY KEY,
    station_id TEXT,
    session_id TEXT,
    failure_date TEXT,
    opened_at_utc TEXT,
    resolved_at_utc TEXT,
    downtime_minutes INTEGER,
    severity TEXT,
    failure_code TEXT,
    symptom_summary TEXT
);

CREATE TABLE fact_maintenance_tickets (
    ticket_id TEXT PRIMARY KEY,
    station_id TEXT,
    failure_event_id TEXT,
    ticket_type TEXT,
    priority TEXT,
    status TEXT,
    opened_at_utc TEXT,
    closed_at_utc TEXT,
    technician_name TEXT,
    resolution_code TEXT,
    summary TEXT
);

CREATE TABLE fact_maintenance_notes (
    note_id TEXT PRIMARY KEY,
    ticket_id TEXT,
    station_id TEXT,
    note_date TEXT,
    note_ts_utc TEXT,
    author_role TEXT,
    sop_reference TEXT,
    parts_used TEXT,
    note_text TEXT
);

CREATE TABLE fact_weather_hourly (
    weather_row_id INTEGER PRIMARY KEY,
    station_group TEXT,
    state TEXT,
    weather_date TEXT,
    observation_ts_utc TEXT,
    temperature_2m REAL,
    apparent_temperature REAL,
    precipitation_probability REAL,
    cloud_cover REAL,
    wind_speed_10m REAL
);

CREATE TABLE fact_energy_hourly (
    energy_row_id INTEGER PRIMARY KEY,
    respondent TEXT,
    state TEXT,
    energy_date TEXT,
    period_utc TEXT,
    value REAL,
    value_type TEXT
);

CREATE TABLE gold_station_daily_metrics (
    station_id TEXT,
    metric_date TEXT,
    state TEXT,
    session_count INTEGER,
    total_energy_kwh REAL,
    total_revenue_usd REAL,
    avg_session_duration_minutes REAL,
    avg_queue_minutes REAL,
    queue_event_count INTEGER,
    failure_event_count INTEGER
);

CREATE TABLE gold_state_daily_demand (
    state TEXT,
    metric_date TEXT,
    session_count INTEGER,
    total_energy_kwh REAL,
    total_revenue_usd REAL,
    avg_temperature_2m REAL,
    avg_precipitation_probability REAL,
    avg_grid_demand_mw REAL
);

CREATE TABLE gold_station_health (
    station_id TEXT,
    state TEXT,
    total_sessions INTEGER,
    total_failures INTEGER,
    total_downtime_minutes INTEGER,
    avg_queue_minutes REAL,
    avg_packet_loss_pct REAL,
    failure_rate_per_100_sessions REAL
);

CREATE TABLE gold_ml_station_day_features (
    station_id TEXT,
    metric_date TEXT,
    state TEXT,
    traffic_segment TEXT,
    port_count INTEGER,
    session_count INTEGER,
    total_energy_kwh REAL,
    avg_queue_minutes REAL,
    queue_event_count INTEGER,
    failure_event_count INTEGER,
    avg_temperature_2m REAL,
    avg_precipitation_probability REAL,
    avg_grid_demand_mw REAL
);
