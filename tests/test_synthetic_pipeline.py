import csv
import unittest
from pathlib import Path

from src.synthetic.pipeline import generate_synthetic_data


class SyntheticPipelineTests(unittest.TestCase):
    def test_generate_synthetic_data_outputs_joinable_files(self) -> None:
        outputs = generate_synthetic_data()

        expected_keys = {
            "augmented_stations",
            "users",
            "vehicles",
            "sessions",
            "telemetry",
            "queue_events",
            "failure_events",
            "maintenance_tickets",
            "maintenance_notes",
            "manifest",
        }
        self.assertEqual(set(outputs.keys()), expected_keys)

        sessions = _read_csv(outputs["sessions"])
        vehicles = _read_csv(outputs["vehicles"])
        stations = _read_csv(outputs["augmented_stations"])
        tickets = _read_csv(outputs["maintenance_tickets"])
        notes = _read_csv(outputs["maintenance_notes"])

        self.assertTrue(sessions)
        self.assertTrue(vehicles)
        self.assertTrue(stations)
        self.assertTrue(tickets)
        self.assertTrue(notes)

        station_ids = {row["station_id"] for row in stations}
        vehicle_ids = {row["vehicle_id"] for row in vehicles}
        ticket_ids = {row["ticket_id"] for row in tickets}

        self.assertTrue(all(row["station_id"] in station_ids for row in sessions))
        self.assertTrue(all(row["vehicle_id"] in vehicle_ids for row in sessions))
        self.assertTrue(all(row["ticket_id"] in ticket_ids for row in notes))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


if __name__ == "__main__":
    unittest.main()
