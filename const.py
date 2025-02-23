"""Constants for the PV Forecast CZ integration."""

DOMAIN = "pvforecast_cz"

CONF_API_KEY = "api_key"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_FORECAST_TYPE = "forecast_type" #Určení typu předpovědi. Sluneční svit (pv), teplota (temp),srážkový úhrn (rain)
CONF_FORECAST_FORMAT = "forecast_format"
CONF_FORECAST_TYPE = "forecast_type" # Hodinové nebo denní sumy
CONF_FORECAST_NUMBER = "forecast_number" #Delka predpovedi v hodinach nebo dnech

MANUFACTURER = "PV Forecast CZ"
MODEL = "API"

DEFAULT_FORECAST_TYPE = "pv"
DEFAULT_FORECAST_FORMAT = "json"
DEFAULT_FORECAST_TIME_TYPE = "day"
DEFAULT_FORECAST_NUMBER = 1

# --- Custom Exceptions ---
class InvalidApiKeyError(Exception):
    """Raised when the API key is invalid."""

class ApiConnectionError(Exception):
    """Raised when there is an error connecting to the API."""

