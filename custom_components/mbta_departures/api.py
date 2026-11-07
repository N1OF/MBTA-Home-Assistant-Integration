"""MBTA V3 transport and pure departure normalization."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import asyncio
from urllib.parse import urlsplit
import aiohttp

BASE = "https://api-v3.mbta.com"
EASTERN = ZoneInfo("America/New_York")

class MBTAError(Exception):
    """An MBTA request failed."""

class InvalidAuth(MBTAError):
    """MBTA rejected the API key."""

def timestamp(value):
    """Parse an offset-aware API timestamp."""
    if not value:
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result if result.tzinfo else None
    except (TypeError, ValueError):
        return None

def rel(item, name):
    return ((item.get("relationships", {}).get(name, {}).get("data") or {}).get("id", ""))

def departures(predictions, schedules, now, limit=10):
    """Merge on trip and stop sequence; retain cancellations and track changes."""
    included = {}
    for document in (schedules, predictions):
        included.update({(x["type"], x["id"]): x.get("attributes", {}) for x in document.get("included", [])})
    merged = {}
    for realtime, document in ((False, schedules), (True, predictions)):
        for item in document.get("data", []):
            attr = item.get("attributes", {})
            trip, stop, route = (rel(item, x) for x in ("trip", "stop", "route"))
            # A platform may change between schedule and prediction.
            key = (trip, attr.get("stop_sequence"), route)
            if realtime and attr.get("schedule_relationship") == "NO_DATA":
                continue
            if realtime:
                merged.pop(key, None)
            if attr.get("schedule_relationship") in ("CANCELLED", "SKIPPED"):
                continue
            # Departure-only board: terminal arrivals without a departure are excluded.
            when = timestamp(attr.get("departure_time"))
            if not when or when < now or when > now + timedelta(hours=3):
                continue
            trip_attrs = included.get(("trip", trip), {})
            merged[key] = {
                "trip_id": trip, "route_id": route, "stop_id": stop,
                "destination": trip_attrs.get("headsign") or route,
                "departure_time": when.isoformat(),
                "track": included.get(("stop", stop), {}).get("platform_code"),
                "realtime": realtime, "direction_id": attr.get("direction_id"),
                "status": attr.get("status"),
            }
    return sorted(merged.values(), key=lambda x: timestamp(x["departure_time"]))

def active_alerts(document, now):
    result = []
    for item in document.get("data", []):
        a = item.get("attributes", {})
        periods = a.get("active_period", [])
        if periods and not any(
            (not timestamp(p.get("start")) or timestamp(p["start"]) <= now)
            and (not timestamp(p.get("end")) or now < timestamp(p["end"])) for p in periods
        ):
            continue
        result.append({"id": item["id"], "header": a.get("header", ""),
                       "description": a.get("description", ""), "severity": a.get("severity"),
                       "effect": a.get("effect"), "url": a.get("url")})
    return result

class MBTAClient:
    def __init__(self, session, api_key=""):
        self.session = session
        self.api_key = api_key

    async def get(self, path, params=None):
        headers = {"Accept": "application/vnd.api+json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        data, included = [], []
        url = BASE + path
        # Bound pagination; fail rather than silently publishing incomplete data.
        for _ in range(30):
            try:
                async with self.session.get(url, params=params, headers=headers,
                                            timeout=aiohttp.ClientTimeout(total=25)) as response:
                    if response.status in (401, 403):
                        raise InvalidAuth("API key rejected")
                    if response.status != 200:
                        raise MBTAError(f"MBTA HTTP {response.status}")
                    payload = await response.json()
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
                raise MBTAError("Unable to retrieve MBTA data") from err
            data.extend(payload.get("data", []))
            included.extend(payload.get("included", []))
            link = payload.get("links", {}).get("next")
            if not link:
                return {"data": data, "included": included}
            url = BASE + link if link.startswith("/") else link
            if urlsplit(url).scheme != "https" or urlsplit(url).netloc != "api-v3.mbta.com":
                raise MBTAError("Unexpected pagination host")
            params = None
        raise MBTAError("MBTA pagination limit exceeded")
