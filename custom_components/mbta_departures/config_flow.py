"""UI configuration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import MBTAClient, MBTAError, InvalidAuth
from .const import DOMAIN, STATIONS

class MBTAConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            if not user_input["stations"]:
                errors["base"] = "no_stations"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                try:
                    await MBTAClient(async_get_clientsession(self.hass), user_input.get("api_key", "")).get(
                        "/predictions", {"filter[stop]": user_input["stations"][0], "page[limit]": "100"})
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except MBTAError:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(title="MBTA Departures", data=user_input)
        return self.async_show_form(step_id="user", data_schema=vol.Schema({
            vol.Optional("api_key", default=""): selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)),
            vol.Required("stations", default=list(STATIONS)): selector.SelectSelector(selector.SelectSelectorConfig(
                options=[{"value": key, "label": name} for key, name in STATIONS.items()], multiple=True)),
            vol.Required("scan_interval", default=60): vol.All(vol.Coerce(int), vol.Range(min=30, max=300)),
        }), errors=errors)

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                await MBTAClient(async_get_clientsession(self.hass), user_input["api_key"]).get(
                    "/predictions", {"filter[stop]": "place-sstat", "page[limit]": "100"})
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except MBTAError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(self._get_reauth_entry(), data_updates=user_input)
        return self.async_show_form(step_id="reauth_confirm", data_schema=vol.Schema({vol.Required("api_key"): str}), errors=errors)
