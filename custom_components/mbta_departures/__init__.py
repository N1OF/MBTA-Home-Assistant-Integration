"""MBTA Departures integration."""
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .coordinator import MBTACoordinator

async def async_setup_entry(hass, entry):
    coordinator = MBTACoordinator(hass, entry, async_get_clientsession(hass))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])
    return True

async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, [Platform.SENSOR])
