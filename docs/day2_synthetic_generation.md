# Day 2 Synthetic Data Notes

## Scope

Day 2 generates realistic operational and behavioral data that joins directly to the real public station layer ingested on Day 1.

## Generated Datasets

- `augmented_stations.csv`
- `users.csv`
- `vehicles.csv`
- `charging_sessions.csv`
- `telemetry_events.csv`
- `queue_events.csv`
- `failure_events.csv`
- `maintenance_tickets.csv`
- `maintenance_notes.csv`
- `generation_manifest.csv`

## Join Strategy

- `source_station_id` keeps the original NREL station identifier.
- `station_id` is the ChargeFlow internal station key derived from the NREL ID.
- `user_id` joins to `vehicles.user_id` and `charging_sessions.user_id`.
- `vehicle_id` joins to `charging_sessions.vehicle_id`.
- `session_id` joins to telemetry and queue events.
- `failure_event_id` joins to maintenance tickets.
- `ticket_id` joins to maintenance notes.

## Synthetic Design Choices

- Generation is deterministic with a fixed random seed from `configs/base.yaml`.
- The pipeline reads the latest Day 1 station payload and builds all synthetic tables from that anchor.
- Text maintenance notes are written as row-level records so they are easy to index later for retrieval and RAG.
- Output files are stored in `data/processed/synthetic/` because they are generated operational data rather than untouched source payloads.

## Run

```bash
python3 -m src.synthetic.cli generate-all
```
