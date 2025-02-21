"""Config flow for PV Forecast CZ integration."""
import logging
_LOGGER = logging.getLogger(__name__)
_LOGGER.debug("Loading config_flow.py...")  # Add this line

from typing import Any
import voluptuous as vol
import logging

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_FORECAST_TYPE,
    CONF_FORECAST_FORMAT,
    CONF_FORECAST_TIME_TYPE,
    CONF_FORECAST_HOURS,
    DEFAULT_FORECAST_TYPE,
    DEFAULT_FORECAST_FORMAT,
    DEFAULT_FORECAST_TIME_TYPE,
    DEFAULT_FORECAST_HOURS,
    InvalidApiKeyError,
    ApiConnectionError,
)

from .sensor import async_fetch_data
_LOGGER.debug("Loading config_flow.py...2") 

class PVForecastCZConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PV Forecast CZ."""

    VERSION = 1
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the API key by making a test API call
            try:
                session = async_get_clientsession(self.hass)
                test_data = await async_fetch_data(
                    session,
                    "https://www.pvforecast.cz/api/",
                    {
                        "key": user_input[CONF_API_KEY],
                        "lat": user_input[CONF_LATITUDE],
                        "lon": user_input[CONF_LONGITUDE],
                        "forecast": DEFAULT_FORECAST_TYPE,
                        "format": DEFAULT_FORECAST_FORMAT,
                        "type": DEFAULT_FORECAST_TIME_TYPE,
                        "number": DEFAULT_FORECAST_HOURS,
                    },
                )

                if test_data is not None:
                    return self.async_create_entry(
                        title=f"PV Forecast CZ ({user_input[CONF_LATITUDE]}, {user_input[CONF_LONGITUDE]})",
                        data=user_input,
                    )
                else:
                    errors["base"] = "unknown" # Pokud async_fetch_data vrátí None z neznámého důvodu
            except InvalidApiKeyError: # Zachytává InvalidApiKeyError
                errors["base"] = "invalid_api_key"
            except ApiConnectionError: # Zachytává ApiConnectionError
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except # Pro neočekávané chyby
                _LOGGER.exception("Unexpected error during API validation")
                errors["base"] = "unknown"
            return self.async_create_entry(
                title=f"PV Forecast CZ ({user_input[CONF_LATITUDE]}, {user_input[CONF_LONGITUDE]})",
                data=user_input,
            )

        # Get default coordinates from HA config
        default_latitude = self.hass.config.latitude
        default_longitude = self.hass.config.longitude

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(
                        CONF_LATITUDE, default=default_latitude
                    ): cv.latitude,
                    vol.Required(
                        CONF_LONGITUDE, default=default_longitude
                    ): cv.longitude,
                    vol.Optional(
                        CONF_FORECAST_TYPE,
                        default=DEFAULT_FORECAST_TYPE,
                    ): vol.In(["pv", "other_type"]),  # Add your valid forecast types
                    vol.Optional(
                        CONF_FORECAST_HOURS,
                        default=DEFAULT_FORECAST_HOURS,
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
                }
            ),
            errors=errors,
        )
