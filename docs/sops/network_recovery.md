# SOP: Network Recovery and Heartbeat Loss

Use this procedure when heartbeat events are missing, packet loss spikes, or the payment terminal cannot reach backend services.

1. Confirm the duration of the heartbeat outage from telemetry.
2. Check controller uptime, modem signal strength, and switch power status.
3. Restart the communications stack before replacing hardware.
4. Validate payment authorization and remote start capability after recovery.
5. Escalate to the network vendor if packet loss remains above 2 percent after reboot.
6. Capture timestamps of outage start, recovery, and any recurring symptoms in the incident notes.
