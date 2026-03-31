INSERT INTO gold_station_daily_metrics
SELECT
    s.station_id,
    s.session_date AS metric_date,
    d.state,
    COUNT(*) AS session_count,
    ROUND(SUM(s.energy_kwh), 2) AS total_energy_kwh,
    ROUND(SUM(s.price_usd), 2) AS total_revenue_usd,
    ROUND(AVG(s.session_duration_minutes), 2) AS avg_session_duration_minutes,
    ROUND(AVG(s.queue_minutes), 2) AS avg_queue_minutes,
    COUNT(DISTINCT q.queue_event_id) AS queue_event_count,
    COUNT(DISTINCT f.failure_event_id) AS failure_event_count
FROM fact_charging_sessions s
JOIN dim_station d
    ON s.station_id = d.station_id
LEFT JOIN fact_queue_events q
    ON s.session_id = q.session_id
LEFT JOIN fact_failure_events f
    ON s.station_id = f.station_id
   AND s.session_date = f.failure_date
GROUP BY s.station_id, s.session_date, d.state;

INSERT INTO gold_state_daily_demand
WITH weather_daily AS (
    SELECT
        state,
        weather_date,
        ROUND(AVG(temperature_2m), 2) AS avg_temperature_2m,
        ROUND(AVG(precipitation_probability), 2) AS avg_precipitation_probability
    FROM fact_weather_hourly
    GROUP BY state, weather_date
),
energy_daily AS (
    SELECT
        state,
        energy_date,
        ROUND(AVG(value), 2) AS avg_grid_demand_mw
    FROM fact_energy_hourly
    GROUP BY state, energy_date
)
SELECT
    d.state,
    s.session_date AS metric_date,
    COUNT(*) AS session_count,
    ROUND(SUM(s.energy_kwh), 2) AS total_energy_kwh,
    ROUND(SUM(s.price_usd), 2) AS total_revenue_usd,
    w.avg_temperature_2m,
    w.avg_precipitation_probability,
    e.avg_grid_demand_mw
FROM fact_charging_sessions s
JOIN dim_station d
    ON s.station_id = d.station_id
LEFT JOIN weather_daily w
    ON d.state = w.state
   AND s.session_date = w.weather_date
LEFT JOIN energy_daily e
    ON d.state = e.state
   AND s.session_date = e.energy_date
GROUP BY d.state, s.session_date, w.avg_temperature_2m, w.avg_precipitation_probability, e.avg_grid_demand_mw;

INSERT INTO gold_station_health
WITH telemetry_summary AS (
    SELECT
        station_id,
        ROUND(AVG(packet_loss_pct), 3) AS avg_packet_loss_pct
    FROM fact_telemetry_events
    GROUP BY station_id
),
failure_summary AS (
    SELECT
        station_id,
        COUNT(*) AS total_failures,
        SUM(downtime_minutes) AS total_downtime_minutes
    FROM fact_failure_events
    GROUP BY station_id
),
session_summary AS (
    SELECT
        station_id,
        COUNT(*) AS total_sessions,
        ROUND(AVG(queue_minutes), 2) AS avg_queue_minutes
    FROM fact_charging_sessions
    GROUP BY station_id
)
SELECT
    d.station_id,
    d.state,
    COALESCE(s.total_sessions, 0) AS total_sessions,
    COALESCE(f.total_failures, 0) AS total_failures,
    COALESCE(f.total_downtime_minutes, 0) AS total_downtime_minutes,
    COALESCE(s.avg_queue_minutes, 0) AS avg_queue_minutes,
    COALESCE(t.avg_packet_loss_pct, 0) AS avg_packet_loss_pct,
    CASE
        WHEN COALESCE(s.total_sessions, 0) = 0 THEN 0
        ELSE ROUND(COALESCE(f.total_failures, 0) * 100.0 / s.total_sessions, 2)
    END AS failure_rate_per_100_sessions
FROM dim_station d
LEFT JOIN session_summary s
    ON d.station_id = s.station_id
LEFT JOIN failure_summary f
    ON d.station_id = f.station_id
LEFT JOIN telemetry_summary t
    ON d.station_id = t.station_id;

INSERT INTO gold_ml_station_day_features
WITH weather_daily AS (
    SELECT
        state,
        weather_date,
        ROUND(AVG(temperature_2m), 2) AS avg_temperature_2m,
        ROUND(AVG(precipitation_probability), 2) AS avg_precipitation_probability
    FROM fact_weather_hourly
    GROUP BY state, weather_date
),
energy_daily AS (
    SELECT
        state,
        energy_date,
        ROUND(AVG(value), 2) AS avg_grid_demand_mw
    FROM fact_energy_hourly
    GROUP BY state, energy_date
)
SELECT
    g.station_id,
    g.metric_date,
    g.state,
    d.traffic_segment,
    d.port_count,
    g.session_count,
    g.total_energy_kwh,
    g.avg_queue_minutes,
    g.queue_event_count,
    g.failure_event_count,
    w.avg_temperature_2m,
    w.avg_precipitation_probability,
    e.avg_grid_demand_mw
FROM gold_station_daily_metrics g
JOIN dim_station d
    ON g.station_id = d.station_id
LEFT JOIN weather_daily w
    ON g.state = w.state
   AND g.metric_date = w.weather_date
LEFT JOIN energy_daily e
    ON g.state = e.state
   AND g.metric_date = e.energy_date;
