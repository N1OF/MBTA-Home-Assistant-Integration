# MBTA black and amber departure board

This dashboard card works with the existing `mbta_departures` integration. There is no backend change. It uses no external card libraries, fonts, or network requests; it reads the integration's entities through Home Assistant.

## Install

1. Copy `www/mbta-departure-board.js` from this ZIP into `/config/www/mbta-departure-board.js` on Home Assistant, using the same Samba share used to install the integration. Create `www` next to `configuration.yaml` if necessary.
2. If you just created `www`, restart Home Assistant once.
3. In your Home Assistant profile, enable Advanced mode if the Resources menu is hidden.
4. Open Settings → Dashboards → top-right three-dot menu → Resources → Add resource.
5. URL: `/local/mbta-departure-board.js?v=1`. Type: **JavaScript module**. Save.
6. Reload your browser. If necessary hard-refresh with Ctrl+Shift+R.
7. Open your MBTA dashboard → Edit dashboard → three-dot menu → Raw configuration editor. Back up your existing YAML first.
8. Replace the dashboard's configuration with all of `dashboard.yaml` from this ZIP and save.

If your dashboard resources are managed in YAML instead of the UI, add the following under your existing `lovelace` configuration (do not duplicate the key), then reload dashboard resources:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /local/mbta-departure-board.js?v=1
      type: module
```

## Appearance and behavior

- Separate South and North Station boards with amber text and a black background.
- All six service groups; small line-color markers.
- Destination, track, departure countdown and Boston departure clock columns.
- Explicit LIVE / SCHEDULED source labels; stale data marked after three minutes.
- Collapsed, keyboard-accessible service alerts. Click or press Enter to expand.
- Refreshes countdowns every 15 seconds, independently of integration polling.
- Expired departures disappear. Exact duplicate trip/route/time/direction rows are suppressed. Schedule/prediction entries with different times require a backend merge correction; this card deliberately does not guess which train is correct.
- Default five departures per service. Edit `rows` (1–20) in dashboard.yaml.
- Responsive widths, wrapped destinations, no flashing animation.
- Times default to Boston; edit `time_zone` per card if desired.

Cards use existing entity IDs from the first integration package. If Home Assistant renamed an entity or appended `_2`, edit the card YAML to match Settings → Devices & services → Entities. The card explicitly shows ENTITY NOT FOUND when an ID does not exist.

## Troubleshooting

**Custom element doesn't exist: mbta-departure-board**: verify the resource URL/type and the file path, then hard-refresh. Open `/local/mbta-departure-board.js?v=1` on your Home Assistant address: it should return JavaScript, not a 404 or login page.

**Old appearance after updating**: replace the JS file, change the resource query to `?v=2`, and reload the browser.

**Unknown/no departures**: the integration may have no departures in its current window. Check sensor attributes in Developer Tools → States. `unavailable` is explicitly shown as offline.

## Share on GitHub

Add the JS file, dashboard.yaml and these instructions under a `frontend/` or `examples/amber-dashboard/` directory in your integration repository. Users still need to copy the card into `www` and register its resource. HACS installing/updating the integration alone will not install this separate frontend resource automatically.

To distribute as a HACS dashboard card with automatic frontend updates, use a separate dashboard-card repository and corresponding HACS configuration. This ZIP is the manual frontend installation package.

## License

MIT; see LICENSE. Community design inspired by station departure signs, not an official MBTA product.
