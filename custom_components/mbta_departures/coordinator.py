"""Shared polling with slower schedule and alert caches."""
from datetime import datetime, timedelta, timezone
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed
from .api import MBTAClient, MBTAError, InvalidAuth, EASTERN, departures, active_alerts
from .const import DOMAIN

class MBTACoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, session):
        super().__init__(hass, logging.getLogger(__name__), name=DOMAIN,
                         update_interval=timedelta(seconds=entry.data["scan_interval"]))
        self.client = MBTAClient(session, entry.data.get("api_key", ""))
        self.stations = entry.data["stations"]
        self.schedules = {}
        self.alerts = {}
        self.cached_at = None

    async def _async_update_data(self):
        now = datetime.now(timezone.utc)
        refresh_cache = self.cached_at is None or now - self.cached_at >= timedelta(minutes=5)
        new_schedules, new_alerts = dict(self.schedules), dict(self.alerts)
        result = {}
        try:
            for station in self.stations:
                params = {"filter[stop]": station, "include": "trip,stop", "page[limit]": "100"}
                pred = await self.client.get("/predictions", params)
                if refresh_cache:
                    combined = {"data": [], "included": []}
                    # Query each calendar date in a 3-hour window, including midnight.
                    end = now + timedelta(hours=3)
                    dates = {now.astimezone(EASTERN).date(), end.astimezone(EASTERN).date()}
                    for day in sorted(dates):
                        schedule = await self.client.get("/schedules", {**params, "filter[date]": day.isoformat(),
                            "filter[min_time]": now.astimezone(EASTERN).strftime("%H:%M:%S") if day == now.astimezone(EASTERN).date() else "00:00:00",
                            "filter[max_time]": end.astimezone(EASTERN).strftime("%H:%M:%S") if day == end.astimezone(EASTERN).date() else "23:59:59"})
                        for key in combined:
                            combined[key].extend(schedule.get(key, []))
                    new_schedules[station] = combined
                    new_alerts[station] = await self.client.get("/alerts", {"filter[stop]": station, "page[limit]": "100"})
                result[station] = {"departures": departures(pred, new_schedules[station], now),
                                   "alerts": active_alerts(new_alerts[station], now),
                                   "updated_at": now.isoformat()}
        except InvalidAuth as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except MBTAError as err:
            raise UpdateFailed(str(err)) from err
        self.schedules, self.alerts = new_schedules, new_alerts
        if refresh_cache:
            self.cached_at = now
        return result
