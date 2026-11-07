"""Departure timestamp and alert count entities."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .api import timestamp
from .const import DOMAIN, STATIONS, SERVICES

async def async_setup_entry(hass, entry, async_add_entities):
    entities = []
    for station in entry.data["stations"]:
        for service in SERVICES[station]:
            entities.append(MBTASensor(entry.runtime_data, station, service))
        entities.append(MBTASensor(entry.runtime_data, station, "alerts"))
    async_add_entities(entities)

class MBTASensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _unrecorded_attributes = frozenset({"departures", "alerts", "updated_at"})

    def __init__(self, coordinator, station, service):
        super().__init__(coordinator)
        self.station, self.service = station, service
        self._attr_unique_id = f"{station}_{service}"
        slug = "south_station" if station == "place-sstat" else "north_station"
        self.entity_id = f"sensor.mbta_{slug}_{service}"
        self._attr_name = "Alerts" if service == "alerts" else SERVICES[station][service][0]
        self._attr_icon = "mdi:alert-circle-outline" if service == "alerts" else "mdi:train"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, station)}, name=f"MBTA {STATIONS[station]}", manufacturer="MBTA")
        if service != "alerts":
            self._attr_device_class = SensorDeviceClass.TIMESTAMP

    def _departures(self):
        rows = self.coordinator.data[self.station]["departures"]
        routes = SERVICES[self.station][self.service][1]
        return [r for r in rows if (r["route_id"].startswith("CR-") if self.service == "rail" else r["route_id"] in routes)][:10]

    @property
    def native_value(self):
        if self.service == "alerts":
            return len(self.coordinator.data[self.station]["alerts"])
        rows = self._departures()
        return timestamp(rows[0]["departure_time"]) if rows else None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data[self.station]
        return {"station": STATIONS[self.station], "updated_at": data["updated_at"],
                **({"alerts": data["alerts"]} if self.service == "alerts" else {"departures": self._departures()})}
