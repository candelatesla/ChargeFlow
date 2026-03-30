from __future__ import annotations

VEHICLE_CATALOG = [
    {"make": "Tesla", "model": "Model 3", "battery_kwh": 60, "connector": "J1772COMBO"},
    {"make": "Ford", "model": "Mustang Mach-E", "battery_kwh": 72, "connector": "J1772COMBO"},
    {"make": "Hyundai", "model": "IONIQ 5", "battery_kwh": 77, "connector": "J1772COMBO"},
    {"make": "Kia", "model": "EV6", "battery_kwh": 77, "connector": "J1772COMBO"},
    {"make": "Nissan", "model": "Leaf", "battery_kwh": 40, "connector": "CHADEMO"},
    {"make": "Chevrolet", "model": "Bolt EUV", "battery_kwh": 65, "connector": "J1772"},
    {"make": "Rivian", "model": "R1S", "battery_kwh": 105, "connector": "J1772COMBO"},
    {"make": "Volkswagen", "model": "ID.4", "battery_kwh": 82, "connector": "J1772COMBO"},
]

USER_SEGMENTS = [
    "daily_commuter",
    "rideshare_driver",
    "fleet_operator",
    "road_trip_driver",
    "apartment_resident",
]

FAILURE_CODES = [
    ("connector_fault", "Connector latch error detected during handshake."),
    ("payment_reader_error", "Payment authorization repeatedly timed out."),
    ("cooling_alarm", "Thermal management exceeded the safe operating threshold."),
    ("network_dropout", "Heartbeat packets dropped for more than five minutes."),
    ("breaker_trip", "Power delivery interrupted after breaker trip."),
]

RESOLUTION_CODES = [
    "reboot_controller",
    "replace_cable",
    "tighten_terminal",
    "update_firmware",
    "reset_payment_terminal",
]

TECHNICIAN_NAMES = [
    "A. Patel",
    "J. Nguyen",
    "M. Garcia",
    "S. Johnson",
    "R. Kim",
]

NOTE_TEMPLATES = [
    "Arrived on site after repeated {failure_code} alerts. Confirmed {symptom} and isolated charger port {port_number}.",
    "Reviewed controller logs and verified issue window matched customer complaints from peak demand period.",
    "Applied resolution step {resolution_code}. Monitored two successful restart cycles before returning asset to service.",
    "Recommended follow-up SOP review for cable inspection and connector cleaning during next preventive maintenance window.",
]
