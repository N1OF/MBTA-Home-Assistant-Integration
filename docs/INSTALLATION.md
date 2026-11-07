# MBTA Departures for Home Assistant

Community custom integration for Boston South Station and North Station. Not affiliated with the MBTA.
Version 0.1.0 is an initial community release. The author reports successful operation in Home Assistant; broader compatibility testing is welcome.

## Features

- UI setup; choose either or both terminals.
- South: Red, Silver and Commuter Rail. North: Orange, Green and Commuter Rail.
- Next departure timestamp sensors, with up to 10 upcoming departures in attributes.
- Real-time predictions override schedules, including platform changes and cancelled/skipped trips.
- Tracks when MBTA supplies platform codes; absence of a track does not imply an error.
- Active station alerts, descriptions and severity.
- Predictions every 60 seconds by default (configurable 30–300 at setup). Schedules and alerts every five minutes.
- Standard Lovelace Markdown dashboard, no extra cards required.

## 1. Obtain an API key

Register at https://api-v3.mbta.com/ . The key is optional, but anonymous requests have stricter rate limits.
Enter your own key in Home Assistant during setup; no key or Wi-Fi credentials belong in this repository.

## 2. Install manually

1. Extract this archive on your computer.
2. Open your Home Assistant configuration directory (the directory containing `configuration.yaml`). With HA OS, use a file editor app or Samba share. Container users use the directory mounted to `/config`.
3. Create `custom_components` if it does not exist.
4. Copy the entire `mbta_departures` folder from this project's `custom_components` into it.
5. Confirm the resulting path is `/config/custom_components/mbta_departures/manifest.json`. Avoid an extra nested project directory.
6. Restart Home Assistant completely.
7. Open **Settings → Devices & services → Add integration**, search **MBTA Departures**.
8. Enter your API key, select both stations and keep 60 seconds initially. Submit.
9. Check the integration's entities. Six departure sensors and two alert sensors should appear when both stations are selected.

No `configuration.yaml` sensor setup is required. If the integration is missing, refresh the browser and check Settings → System → Logs.

## 3. Create the dashboard

1. Open **Settings → Dashboards → Add dashboard** and create a new empty dashboard named MBTA. If offered a built-in dashboard type, choose to create your own.
2. Open that dashboard, choose **Edit dashboard** and take control if prompted.
3. Open its three-dot menu → **Raw configuration editor**.
4. Replace the empty dashboard configuration with all of `examples/dashboard.yaml`, then save.
5. The dashboard shows station/service headings, destinations, local departure times, minute countdowns, tracks, live/scheduled labels and alerts.

The example assumes these initial entity IDs:

| Station | Entity IDs |
| --- | --- |
| South | `sensor.mbta_south_station_red`, `sensor.mbta_south_station_silver`, `sensor.mbta_south_station_rail`, `sensor.mbta_south_station_alerts` |
| North | `sensor.mbta_north_station_orange`, `sensor.mbta_north_station_green`, `sensor.mbta_north_station_rail`, `sensor.mbta_north_station_alerts` |

If Home Assistant appends `_2` or you rename an entity, replace that ID in the dashboard YAML. Countdowns update approximately once per minute. Times follow your Home Assistant timezone: select America/New_York if you want Boston local times.

## 4. Publish on GitHub

1. Choose a GitHub username and create a **public**, empty repository named `ha-mbta-departures`. Enable Issues. Do not initialize it with a README or license; this project includes both.
2. Replace both `YOUR_USERNAME` placeholders in `custom_components/mbta_departures/manifest.json` with your GitHub username. Add your actual handle to `codeowners`, e.g. `["@yourname"]`.
3. Add a repository description and topics such as `home-assistant`, `hacs`, `mbta`, `transit`.
4. On your Linux PC, open a terminal in the extracted `ha-mbta-departures` directory and run:

```bash
git init
git add .
git commit -m "Initial MBTA Departures integration"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ha-mbta-departures.git
git push -u origin main
```

Authenticate using your usual GitHub method; GitHub HTTPS pushes use a token or credential manager, not your account password. Alternatively use GitHub's **Add file → Upload files**; upload the project contents, including `.github`, at the repository root. The root must contain `custom_components`, not another `ha-mbta-departures` folder.

5. Check **Actions**. Fix any failures before describing the package as validated. The included workflow runs pure parser tests and Home Assistant hassfest; it does not perform a live HA installation test.
6. Test locally through a full restart, confirm real departures and alerts, then create **Releases → Draft a new release**. Use tag `v0.1.0`, title `MBTA Departures 0.1.0`, and publish as a **pre-release** until real-world validation is complete. A GitHub release is separate from a tag.
7. Share the repository URL and installation instructions.

## 5. Install through HACS after publishing

1. Open HACS in Home Assistant.
2. Open its menu → **Custom repositories**.
3. Enter your full repository URL and select **Integration** as the type.
4. Add it, find **MBTA Departures**, download, and restart Home Assistant.
5. Add the integration using Settings → Devices & services as above.

This is custom-repository distribution, not acceptance into the default HACS catalog. For default listing, review current HACS requirements, add branding through home-assistant/brands, add/pass the HACS action plus hassfest, publish a release and submit to hacs/default. See https://www.hacs.dev/docs/publish/integration/ and https://hacs.dev/docs/publish/include/ .

## Updates and removal

For manual updates replace the component folder and restart. For HACS, download the update and restart. Keep `version` in manifest.json aligned with GitHub release tags. To change station selections or polling interval in this initial version, delete the integration entry and add it again; entity unique IDs remain stable. API authentication failures provide a reauthentication flow.

To remove: delete the integration entry, remove the component folder, then restart. Remove dashboard cards separately.

## Data and limitations

- This is a **departure** board; terminal arrivals with no departure time are excluded.
- Station alerts include accessibility and other notices when MBTA associates them with the selected stop. This is not a systemwide alert feed.
- Only services actually serving each terminal appear. The Silver category includes route IDs 741/742/743/749/751; a route without predictions or schedules at South Station will not appear.
- The next three hours are queried. Schedule fallback is not a promise a train is operating. Live service disruption information takes precedence in trip planning.
- The schedule query covers Boston calendar dates across midnight. MBTA service-day edge cases remain a real-world validation item.
- A failed update makes entities unavailable through the coordinator; old data should not be interpreted as current. Rate-limit responses retry on the normal polling interval.
- The integration uses Home Assistant's shared HTTP session and has no additional pip requirements. Pagination is followed on MBTA's HTTPS host, with a safety bound.
- Large departure/alert attributes are excluded from recording by the entities. No ESP32 changes are included.
- Target Home Assistant: 2025.1 or newer; verify your specific version before public stable release.

## Development

```bash
python -m pip install aiohttp
python -m unittest discover -s tests -v
python -m compileall -q custom_components
```

Local validation covers merge logic, cancellations, timestamp offsets, terminal arrivals and active alerts. Config flow, entity lifecycle, dashboard rendering and MBTA live networking still require testing in Home Assistant. Please include your HA version and sanitized logs in issues, never an API key.

MIT licensed. API documentation: https://api-v3.mbta.com/docs/swagger/swagger.json .

## First-install verification checklist

- All eight sensors exist when both stations are selected.
- During service hours compare displayed destination/time with MBTA's official station pages.
- Confirm tracks are shown when supplied and schedule rows are labeled Schedule.
- Confirm the dashboard identifies both stations and all six services.
- Restart Home Assistant and confirm the integration loads again without setup.
- Check logs for HTTP errors, rate limits or entity exceptions.
- Test deletion and re-addition before publishing a stable release.
