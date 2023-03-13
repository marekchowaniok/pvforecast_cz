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
NATIVE_UNIT_OF_MEASUREMENT = "W/m²"
DEVICE_CLASS = "irradiance"
# STATE_CLASS = "measurement"
state_class = "measurement"


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
        self._forecast_data = dict()
        self._last_forecast_update = None
        self._available = False

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'PV Forecast Sensor'

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
        if self._available == False or self._last_forecast_update is None or (self._last_forecast_update - datetime.datetime.now()).seconds < 8*3600:
            self._update_forecast_data()
        
        #set forecast for the current hour as sensor current value
        current_time = datetime.datetime.now()
        current_hour = datetime.datetime(current_time.year, current_time.month, current_time.day, current_time.hour)
        if str(current_hour) in self._forecast_data:
            self._value = self._forecast_data[str(current_hour)]
        else:
            #_LOGGER.warning(f"Cannot find forecast for '{current_hour}' hour.")
            pass
        
        #_LOGGER.info(f"Updated PVforecast (now={current_time}): {self._forecast_data}")


    def _update_forecast_data(self):
        """ 
        Parse the data and return forecast
        This should be called only once/twice a day!
        """

        try:
            params = dict (
                key="havnhz",
                lat=50.159,
                lon=15.818,
                forecast="pv",
                format="json",
                type="hour",
                number=72,
            )
            url = "http://www.pvforecast.cz/api/"

            response = requests.get(url=url, params=params)
            json = response.json()

            for date, solar in json:
                self._forecast_data[date] = solar
            
            #remove old data in past
            cur_time = datetime.datetime.now()
            to_delete = []
            for date in self._forecast_data:
                if datetime.datetime.fromisoformat(date) < cur_time:
                    to_delete.append(date)
            for date in to_delete:
                del self._forecast_data[date]

            self._attr = self._forecast_data
            self._last_forecast_update = cur_time
            self._available = True
            _LOGGER.info(f"Retrieved new PVforecast data from '{url}': {self._forecast_data}")
        except:
            self._available = False
            cur_time = datetime.datetime.now()
            self._last_forecast_update = cur_time
            _LOGGER.exception("Error occured while retrieving data from pvforecast.cz.")
