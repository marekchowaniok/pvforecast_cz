"""The PV Forecast CZ integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PV Forecast CZ from a config entry."""
    # Forward the setup to the sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True
