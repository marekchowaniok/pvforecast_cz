"""Constants for the PV Forecast CZ integration."""

DOMAIN = "pvforecast_cz"

CONF_API_KEY = "api_key"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_FORECAST_TYPE = "forecast_type"
CONF_FORECAST_FORMAT = "forecast_format"
CONF_FORECAST_TIME_TYPE = "forecast_time_type"
CONF_FORECAST_HOURS = "forecast_hours"

DEFAULT_FORECAST_TYPE = "pv"
DEFAULT_FORECAST_FORMAT = "json"
DEFAULT_FORECAST_TIME_TYPE = "hour"
DEFAULT_FORECAST_HOURS = 72

# --- Custom Exceptions ---
class InvalidApiKeyError(Exception):
    """Raised when the API key is invalid."""

class ApiConnectionError(Exception):
    """Raised when there is an error connecting to the API."""

# ... any other constants you might need ...
