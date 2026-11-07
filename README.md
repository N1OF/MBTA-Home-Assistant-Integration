# MBTA Departures for Home Assistant

Live departure information for Boston **South Station** and **North Station**, with an optional black-and-amber electronic departure board.

Community project by Scott Sheets. Not affiliated with or endorsed by the MBTA.

## Features

| Station | Services |
| --- | --- |
| South Station | Red Line, Silver Line, Commuter Rail |
| North Station | Orange Line, Green Line, Commuter Rail |

- Configure station selections and polling interval in the Home Assistant UI.
- Six next-departure timestamp sensors and two station alert sensors when both terminals are enabled.
- Up to ten upcoming departures per service in sensor attributes.
- Real-time predictions with scheduled fallback; track/platform information when published.
- Active service alerts with descriptions and severity.
- Amber dashboard with fixed columns, countdowns, Boston clock times and expandable alerts.
- No external frontend dependencies or additional Python requirements beyond Home Assistant.

## Install the integration

1. Copy `custom_components/mbta_departures` into your Home Assistant configuration directory's `custom_components` folder.
2. Restart Home Assistant.
3. Open **Settings → Devices & services → Add integration → MBTA Departures**.
4. Enter an optional [MBTA API key](https://api-v3.mbta.com/), select stations and choose the polling interval (default 60 seconds).

The final manifest path should be `/config/custom_components/mbta_departures/manifest.json`. Anonymous MBTA API access has stricter rate limits.

### HACS custom repository

Add this repository's URL in **HACS → Custom repositories**, type **Integration**, download and restart Home Assistant. This is custom-repository distribution; it does not imply acceptance into the default HACS catalog.

## Install the amber dashboard

1. Copy `frontend/www/mbta-departure-board.js` to `/config/www/mbta-departure-board.js`.
2. Restart Home Assistant if you just created the `www` folder.
3. Open **Settings → Dashboards → menu → Resources**. Add `/local/mbta-departure-board.js?v=1` as a **JavaScript module**.
4. Hard-refresh your browser.
5. Create a dashboard and paste `frontend/dashboard.yaml` into its **Raw configuration editor**.

The integration and dashboard card are separate installation steps. HACS integration updates do **not** automatically install or update this frontend file. The standard-card alternative is `examples/dashboard.yaml`.

See [frontend installation and troubleshooting](frontend/INSTALL.md) and [integration installation details](docs/INSTALLATION.md).

## Entity IDs

| Service | South Station | North Station |
| --- | --- | --- |
| Red / Orange | `sensor.mbta_south_station_red` | `sensor.mbta_north_station_orange` |
| Silver / Green | `sensor.mbta_south_station_silver` | `sensor.mbta_north_station_green` |
| Commuter Rail | `sensor.mbta_south_station_rail` | `sensor.mbta_north_station_rail` |
| Alerts | `sensor.mbta_south_station_alerts` | `sensor.mbta_north_station_alerts` |

Adjust dashboard YAML if your actual entity IDs differ. Departure sensor states are timestamps; their `departures` attributes hold the rows used by the dashboard.

## Configuration and data

Predictions refresh every 60 seconds by default (30–300 configurable at setup). Schedules and alerts refresh every five minutes. The departure horizon is three hours. Change selected stations or interval by removing and adding the integration in this initial version. Reauthentication is supported when MBTA rejects a key.

Terminal arrivals without departure times are excluded. Platform assignments and real-time information depend on MBTA availability. Scheduled departures may be affected by disruptions. Station alerts include accessibility notices and are not a systemwide feed. Around-midnight service-day behavior remains a validation area.

## Status and development

Initial release **0.1.0**. The author reports the integration and amber dashboard working in their Home Assistant installation. Parser regression tests and frontend logic checks have passed locally; broad Home Assistant version compatibility has not been independently verified. The current HACS metadata declares Home Assistant 2025.1 or newer as the intended target.

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python -m compileall -q custom_components
node --check frontend/www/mbta-departure-board.js
node tests/test_frontend.cjs
```

[Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Publishing a release](docs/RELEASING.md)

## License

Copyright (c) 2026 Scott Sheets. Released under the [MIT License](LICENSE), covering the integration, dashboard card, examples and documentation. MBTA names and branding identify the transit service and do not imply endorsement.
