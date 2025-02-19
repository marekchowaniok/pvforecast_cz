"""Platform for sensor integration."""
import asyncio
import datetime
import logging

import aiohttp
import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_FORECAST_TYPE,
    CONF_FORECAST_FORMAT,
    CONF_FORECAST_TIME_TYPE,
    CONF_FORECAST_HOURS,
)

_LOGGER = logging.getLogger(__name__)

# --- Constants ---
API_URL = "http://www.pvforecast.cz/api/"
DEFAULT_FORECAST_TYPE = "pv"
DEFAULT_FORECAST_FORMAT = "json"
DEFAULT_FORECAST_TIME_TYPE = "hour"
DEFAULT_FORECAST_HOURS = 72

# --- Sensor Entity Descriptions ---
SENSOR_DESCRIPTIONS = (
    SensorEntityDescription(
        key="pv_forecast",
        name="PV Forecast",
        native_unit_of_measurement="W/m²",
        device_class="irradiance",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

# --- Configuration Schema ---
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_LATITUDE): cv.latitude,
    vol.Required(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_FORECAST_TYPE, default=DEFAULT_FORECAST_TYPE): cv.string,
    vol.Optional(CONF_FORECAST_FORMAT, default=DEFAULT_FORECAST_FORMAT): cv.string,
    vol.Optional(CONF_FORECAST_TIME_TYPE, default=DEFAULT_FORECAST_TIME_TYPE): cv.string,
    vol.Optional(CONF_FORECAST_HOURS, default=DEFAULT_FORECAST_HOURS): cv.positive_int,
})

# --- Setup ---
async def async_setup_platform(
    hass: HomeAssistant,
    config,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
):
    """Set up the sensor platform from a config entry."""
    api_key = config.get(CONF_API_KEY)
    latitude = config.get(CONF_LATITUDE)
    longitude = config.get(CONF_LONGITUDE)
    forecast_type = config.get(CONF_FORECAST_TYPE)
    forecast_format = config.get(CONF_FORECAST_FORMAT)
    forecast_time_type = config.get(CONF_FORECAST_TIME_TYPE)
    forecast_hours = config.get(CONF_FORECAST_HOURS)

    session = aiohttp.ClientSession()

    sensors = []
    for description in SENSOR_DESCRIPTIONS:
        sensors.append(
            PVForecastCZSensor(
                session,
                api_key,
                latitude,
                longitude,
                forecast_type,
                forecast_format,
                forecast_time_type,
                forecast_hours,
                description,
            )
        )

    async_add_entities(sensors, update_before_add=True)

# --- Sensor Entity ---
class PVForecastCZSensor(SensorEntity):
    """Representation of a PV Forecast CZ sensor."""

    def __init__(
        self,
        session,
        api_key,
        latitude,
        longitude,
        forecast_type,
        forecast_format,
        forecast_time_type,
        forecast_hours,
        entity_description: SensorEntityDescription,
    ):
        """Initialize the sensor."""
        self.session = session
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.forecast_type = forecast_type
        self.forecast_format = forecast_format
        self.forecast_time_type = forecast_time_type
        self.forecast_hours = forecast_hours
        self.entity_description = entity_description

        self._value = None
        self._forecast_data = {}
        self._last_forecast_update = None
        self._last_data_update = None
        self._available = False

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    async def async_added_to_hass(self):
        """Handle when the entity is added to Home Assistant."""
        self.async_on_remove(
            async_track_time_interval(
                self.hass, self._async_scheduled_update, datetime.timedelta(hours=1)
            )
        )

    async def _async_scheduled_update(self, now: datetime.datetime):
        """Perform a scheduled update."""
        await self._async_update_forecast_data()
        self.async_write_ha_state()

    async def async_update(self):
        """Update the sensor value and fetch new forecast data if needed."""
        current_hour_str = str(datetime.datetime.now().replace(minute=0, second=0, microsecond=0))
        if current_hour_str in self._forecast_
            self._value = self._forecast_data[current_hour_str]
            self._available = True
        else:
            self._value = None
            self._available = False

    async def _async_update_forecast_data(self):
        """Fetch new forecast data from the API."""
        params = {
            "key": self.api_key,
            "lat": self.latitude,
            "lon": self.longitude,
            "forecast": self.forecast_type,
            "format": self.forecast_format,
            "type": self.forecast_time_type,
            "number": self.forecast_hours,
        }

        try:
            json_data = await async_fetch_data(self.session, API_URL, params)
            if json_data is not None:
                self._forecast_data = {}  # Clear existing data
                for date, solar in json_data.items():
                    self._forecast_data[date] = solar
                self._cleanup_forecast_data() # Cleanup after new data is loaded
                self._last_forecast_update = datetime.datetime.now()
                self._available = True
                _LOGGER.info(
                    "Retrieved new PVforecast data from %s: %s",
                    API_URL,
                    self._forecast_data,
                )
            else:
                _LOGGER.warning("No data received from PVforecast API. Check API response or connection.")
                self._available = False # Set availability to False if no data
        except aiohttp.ClientError as e:
            _LOGGER.error("Connection error while fetching PV forecast: %s", e)
            self._available = False
        except ValueError as e:
            _LOGGER.error("Error parsing JSON  %s", e)
            self._available = False
        except Exception as e:
            _LOGGER.exception("An unexpected error occurred: %s", e)
            self._available = False

    def _cleanup_forecast_data(self):
        """Removes past entries from the forecast data."""
        now = datetime.datetime.now()
        to_delete = [
            date
            for date in self._forecast_data
            if datetime.datetime.fromisoformat(date) < now
        ]
        for date in to_delete:
            del self._forecast_data[date]

async def async_fetch_data(session, url, params):
    """
    Fetches JSON data from the API asynchronously.

    Args:
        session: aiohttp ClientSession.
        url: API URL to fetch data from.
        params: Dictionary of parameters to send with the request.

    Returns:
        JSON response from the API if successful, None otherwise.
    """
    async with session.get(url, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            _LOGGER.error(f"Error fetching  {response.status}, URL: {url}, Params: {params}") # Added URL and params to log
            return None
