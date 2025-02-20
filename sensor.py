"""Platform for sensor integration."""
import datetime
import logging
from typing import Any, Optional

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
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    CONF_FORECAST_TYPE,
    CONF_FORECAST_FORMAT,
    CONF_FORECAST_TIME_TYPE,
    CONF_FORECAST_HOURS,
    MANUFACTURER,
    MODEL,
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
    vol.Optional(
        CONF_FORECAST_TYPE, default=DEFAULT_FORECAST_TYPE
    ): cv.string,
    vol.Optional(
        CONF_FORECAST_FORMAT, default=DEFAULT_FORECAST_FORMAT
    ): cv.string,
    vol.Optional(
        CONF_FORECAST_TIME_TYPE, default=DEFAULT_FORECAST_TIME_TYPE
    ): cv.string,
    vol.Optional(
        CONF_FORECAST_HOURS, default=DEFAULT_FORECAST_HOURS
    ): cv.positive_int,
})

async def async_setup_platform(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[dict[str, Any]] = None,
) -> None:
    """Set up the sensor platform from a config entry."""
    api_key = config[CONF_API_KEY]
    latitude = config[CONF_LATITUDE]
    longitude = config[CONF_LONGITUDE]
    forecast_type = config[CONF_FORECAST_TYPE]
    forecast_format = config[CONF_FORECAST_FORMAT]
    forecast_time_type = config[CONF_FORECAST_TIME_TYPE]
    forecast_hours = config[CONF_FORECAST_HOURS]

    session = async_get_clientsession(hass)

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

class PVForecastCZSensor(SensorEntity):
    """Representation of a PV Forecast CZ sensor."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str,
        latitude: float,
        longitude: float,
        forecast_type: str,
        forecast_format: str,
        forecast_time_type: str,
        forecast_hours: int,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = entity_description
        self._attr_unique_id = f"pvforecast_cz_{latitude}_{longitude}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"pvforecast_cz_{latitude}_{longitude}")},
            name="PV Forecast CZ",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )
        
        self.session = session
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.forecast_type = forecast_type
        self.forecast_format = forecast_format
        self.forecast_time_type = forecast_time_type
        self.forecast_hours = forecast_hours

        self._attr_native_value = None
        self._forecast_ dict[str, float] = {}
        self._last_forecast_update: Optional[datetime.datetime] = None
        self._attr_available = False

    async def async_added_to_hass(self) -> None:
        """Handle when the entity is added to Home Assistant."""
        self.async_on_remove(
            async_track_time_interval(
                self.hass, self._async_scheduled_update, datetime.timedelta(hours=1)
            )
        )

    async def _async_scheduled_update(self, now: datetime.datetime) -> None:
        """Perform a scheduled update."""
        await self._async_update_forecast_data()
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update the sensor value and fetch new forecast data if needed."""
        current_hour_str = datetime.datetime.now().replace(
            minute=0, second=0, microsecond=0
        ).isoformat()
        
        if current_hour_str in self._forecast_
            self._attr_native_value = self._forecast_data[current_hour_str]
            self._attr_available = True
        else:
            self._attr_native_value = None
            self._attr_available = False

    async def _async_update_forecast_data(self) -> None:
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
                    self._forecast_data[date] = float(solar)  # Ensure numeric type
                self._cleanup_forecast_data()
                self._last_forecast_update = datetime.datetime.now()
                self._attr_available = True
                _LOGGER.debug(
                    "Retrieved new PVforecast data from %s: %s",
                    API_URL,
                    self._forecast_data,
                )
            else:
                _LOGGER.warning("No data received from PVforecast API")
                self._attr_available = False
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error while fetching PV forecast: %s", err)
            self._attr_available = False
        except ValueError as err:
            _LOGGER.error("Error parsing JSON: %s", err)
            self._attr_available = False
        except Exception as err:
            _LOGGER.exception("An unexpected error occurred: %s", err)
            self._attr_available = False

    def _cleanup_forecast_data(self) -> None:
        """Remove past entries from the forecast data."""
        now = datetime.datetime.now()
        to_delete = [
            date
            for date in self._forecast_data
            if datetime.datetime.fromisoformat(date) < now
        ]
        for date in to_delete:
            del self._forecast_data[date]

async def async_fetch_data(
    session: aiohttp.ClientSession,
    url: str,
    params: dict[str, Any]
) -> Optional[dict[str, Any]]:
    """Fetch JSON data from the API asynchronously."""
    try:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()

            _LOGGER.error(
                "Error fetching  %s, URL: %s, Params: %s",
                response.status,
                url,
                params,
            )
            return None
    except aiohttp.ClientError as err:
        _LOGGER.error("Connection error: %s", err)

