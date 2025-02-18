# PVForecast CZ Custom Component for Home Assistant

[![HACS Default](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/default)

This Home Assistant custom component integrates with [PVForecast.cz](http://www.pvforecast.cz/) to provide solar power forecasts for your location in Czech Republic and Slovakia.

[PVForecast.cz](http://www.pvforecast.cz/) is a service that provides detailed solar power forecasts for the Czech Republic and Slovakia, utilizing advanced meteorological models to predict solar irradiance. This integration allows you to easily access this data within your Home Assistant setup.

## Features

*   Retrieves current solar power forecast data from PVForecast.cz API.
*   Configurable location (latitude and longitude).
*   Configurable API key.
*   Provides forecast data as a sensor in Home Assistant, displaying irradiance in W/m².
*   Regularly updates forecast data to ensure you have the latest predictions.
*   Supports configurable forecast parameters such as forecast type, format, time type, and forecast hours.

## Installation

### Installation via HACS (Recommended)

1.  Ensure you have [HACS](https://hacs.xyz/) installed in your Home Assistant instance.
2.  Navigate to the HACS "Integrations" section.
3.  Click the "+ Explore & Download Repositories" button at the bottom right.
4.  Search for "PVForecast CZ sensor" and click on the integration card.
5.  Click "Download" in the bottom right corner of the integration card.
6.  Restart Home Assistant to complete the installation.

### Manual Installation

1.  Download the latest release ZIP file from [GitHub Releases](https://github.com/marekchowaniok/pvforecast_cz/releases).
2.  Extract the ZIP file.
3.  Copy the `custom_components/pvforecast_cz` folder into the `<config dir>/custom_components` directory of your Home Assistant installation.
4.  Restart Home Assistant.

## Configuration

To configure the PVForecast CZ sensor, you need to add it to your Home Assistant configuration. Configuration is done via `configuration.yaml` file. Add the following to your `configuration.yaml` file:

