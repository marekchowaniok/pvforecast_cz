"""Config flow for PV Forecast CZ integration."""
import logging
from typing import Any, Optional

import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
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
    DEFAULT_FORECAST_HOURS
)

_LOGGER = logging.getLogger(__name__)

# --- API URL ---
API_URL = "http://www.pvforecast.cz/api/"

async def validate_input(hass, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    session = async_get_clientsession(hass)
    params = {
        "key": data[CONF_API_KEY],
        "lat": data[CONF_LATITUDE],
        "lon": data[CONF_LONGITUDE],
        "forecast": data.get(CONF_FORECAST_TYPE, DEFAULT_FORECAST_TYPE),
        "format": data.get(CONF_FORECAST_FORMAT, DEFAULT_FORECAST_FORMAT),
        "type": data.get(CONF_FORECAST_TIME_TYPE, DEFAULT_FORECAST_TIME_TYPE),
        "number": data.get(CONF_FORECAST_HOURS, DEFAULT_FORECAST_HOURS),
    }

    try:
        async with session.get(API_URL, params=params) as response:
            if response.status != 200:
                raise CannotConnect(f"API returned status code {response.status}")
            await response.json()  # Check if response is valid JSON
    except aiohttp.ClientError as e:
        raise CannotConnect(str(e))
    except Exception as e:
        raise CannotConnect(str(e))

    # Return info that you want to store in the config entry.
    return {"title": "PV Forecast CZ"}

class PVForecastCZConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PV Forecast CZ."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
                return self.async_create_entry(
                    title=user_input.get("title", "PV Forecast CZ"), data=user_input
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): cv.string,
            vol.Required(CONF_LATITUDE): cv.latitude,
            vol.Required(CONF_LONGITUDE): cv.longitude,
            vol.Optional(CONF_FORECAST_TYPE, default=DEFAULT_FORECAST_TYPE): cv.string,
            vol.Optional(CONF_FORECAST_FORMAT, default=DEFAULT_FORECAST_FORMAT): cv.string,
            vol.Optional(CONF_FORECAST_TIME_TYPE, default=DEFAULT_FORECAST_TIME_TYPE): cv.string,
            vol.Optional(CONF_FORECAST_HOURS, default=DEFAULT_FORECAST_HOURS): cv.positive_int,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
