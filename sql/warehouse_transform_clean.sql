INSERT INTO dim_station (
    station_id,
    source_station_id,
    station_name,
    network,
    city,
    state,
    access_code,
    connector_types,
    port_count,
    site_power_kw,
    traffic_segment,
    traffic_score,
    station_age_years
)
SELECT
    s.station_id,
    s.source_station_id,
    COALESCE(s.station_name, r.station_name),
    COALESCE(s.network, r.ev_network),
    COALESCE(s.city, r.city),
    COALESCE(s.state, r.state),
    COALESCE(s.access_code, r.access_code),
    s.connector_types,
    s.port_count,
    s.site_power_kw,
    s.traffic_segment,
    s.traffic_score,
    s.station_age_years
FROM stage_augmented_stations s
LEFT JOIN stage_raw_stations r
    ON s.source_station_id = r.source_station_id;

INSERT INTO dim_user
SELECT
    NULL,
    user_id,
    home_state,
    driver_segment,
    charging_frequency,
    preferred_arrival_window,
    range_anxiety_score,
    price_sensitivity_score,
    reliability_sensitivity_score
FROM stage_users;

INSERT INTO dim_vehicle
SELECT
    NULL,
    vehicle_id,
    user_id,
    make,
    model,
    connector_type,
    battery_kwh,
    efficiency_wh_per_mile,
    max_charge_power_kw,
    home_state
FROM stage_vehicles;

INSERT INTO fact_charging_sessions
SELECT
    session_id,
    station_id,
    user_id,
    vehicle_id,
    substr(session_start_utc, 1, 10) AS session_date,
    session_start_utc,
    session_end_utc,
    session_duration_minutes,
    energy_kwh,
    queue_minutes,
    CASE WHEN peak_period_flag = 'true' THEN 1 ELSE 0 END AS peak_period_flag,
    price_usd,
    start_soc_pct,
    end_soc_pct,
    weather_impact_label
FROM stage_charging_sessions;

INSERT INTO fact_telemetry_events
SELECT
    telemetry_id,
    station_id,
    session_id,
    event_ts_utc,
    heartbeat_status,
    power_kw,
    voltage,
    current_amps,
    connector_temperature_c,
    packet_loss_pct
FROM stage_telemetry_events;

INSERT INTO fact_queue_events
SELECT
    queue_event_id,
    station_id,
    session_id,
    substr(event_ts_utc, 1, 10) AS queue_date,
    event_ts_utc,
    queue_depth,
    estimated_wait_minutes,
    queue_reason
FROM stage_queue_events;

INSERT INTO fact_failure_events
SELECT
    failure_event_id,
    station_id,
    session_id,
    substr(opened_at_utc, 1, 10) AS failure_date,
    opened_at_utc,
    resolved_at_utc,
    downtime_minutes,
    severity,
    failure_code,
    symptom_summary
FROM stage_failure_events;

INSERT INTO fact_maintenance_tickets
SELECT
    ticket_id,
    station_id,
    failure_event_id,
    ticket_type,
    priority,
    status,
    opened_at_utc,
    closed_at_utc,
    technician_name,
    resolution_code,
    summary
FROM stage_maintenance_tickets;

INSERT INTO fact_maintenance_notes
SELECT
    note_id,
    ticket_id,
    station_id,
    substr(note_ts_utc, 1, 10) AS note_date,
    note_ts_utc,
    author_role,
    sop_reference,
    parts_used,
    note_text
FROM stage_maintenance_notes;

INSERT INTO fact_weather_hourly
SELECT
    weather_row_id,
    station_group,
    state,
    substr(observation_ts_utc, 1, 10) AS weather_date,
    observation_ts_utc,
    temperature_2m,
    apparent_temperature,
    precipitation_probability,
    cloud_cover,
    wind_speed_10m
FROM stage_raw_weather_hourly;

INSERT INTO fact_energy_hourly
SELECT
    energy_row_id,
    respondent,
    state,
    substr(period_utc, 1, 10) AS energy_date,
    period_utc,
    value,
    value_type
FROM stage_raw_energy_hourly;
