"""Platform for sensor integration."""
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (
    DEVICE_CLASS_MONETARY,
    SensorEntity,
    SensorEntityDescription,
)

""" External Imports """
import requests
import json
import datetime
import logging


""" Constants """
NATIVE_UNIT_OF_MEASUREMENT = "W/m^2"
DEVICE_CLASS = "monetary"

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities([PVForecastCZSensor()], update_before_add=True)


class PVForecastCZSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._value = None
        self._attr = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Current OTE Energy Cost'

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._value

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement."""
        return NATIVE_UNIT_OF_MEASUREMENT

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS

    @property
    def extra_state_attributes(self):
        """Return other attributes of the sensor."""
        return self._attr

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._get_current_value()


    def _get_current_value(self):
        """ 
        Parse the data and return forecast
        """

        try:
            params = dict (
                key="l71h9m"
                lat=48.965
                lon=16.597
                forecast="pv"
                format="json"
                type="hour"
                number=48
            )
            url = "http://www.pvforecast.cz/api/"

            date = datetime.datetime.now()

            response = requests.get(url=url, params=params)
            json = response.json()

            forecast = dict()
            for date, solar in json:
                forecast[date] = solar

            self._value = 0
            self._attr = forecast
            self._available = True
        except:
            self._available = False
            _LOGGER.exception("Error occured while retrieving data from pvforecast.cz.")
