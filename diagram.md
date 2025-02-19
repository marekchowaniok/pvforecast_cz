graph LR
subgraph const.py
    const_py([const.py])
    DOMAIN
    CONF_API_KEY
    CONF_LATITUDE
    CONF_LONGITUDE
    CONF_FORECAST_TYPE
    CONF_FORECAST_FORMAT
    CONF_FORECAST_TIME_TYPE
    CONF_FORECAST_HOURS
    const_py -- Defines constants --> DOMAIN
    const_py -- Defines constants --> CONF_API_KEY
    const_py -- Defines constants --> CONF_LATITUDE
    const_py -- Defines constants --> CONF_LONGITUDE
    const_py -- Defines constants --> CONF_FORECAST_TYPE
    const_py -- Defines constants --> CONF_FORECAST_FORMAT
    const_py -- Defines constants --> CONF_FORECAST_TIME_TYPE
    const_py -- Defines constants --> CONF_FORECAST_HOURS
end

subgraph __init__.py
    init_py([__init__.py])
    async_setup_entry_init[/async_setup_entry/]
    init_py -- Contains --> async_setup_entry_init
end

subgraph sensor.py
    sensor_py([sensor.py])
    PLATFORM_SCHEMA
    SENSOR_DESCRIPTIONS
    async_setup_platform_sensor[/async_setup_platform/]
    PVForecastCZSensor_class[/PVForecastCZSensor/]
    async_fetch_data_sensor[/async_fetch_data/]
    sensor_py -- Contains --> PLATFORM_SCHEMA
    sensor_py -- Contains --> SENSOR_DESCRIPTIONS
    sensor_py -- Contains --> async_setup_platform_sensor
    sensor_py -- Contains --> PVForecastCZSensor_class
    sensor_py -- Contains --> async_fetch_data_sensor
end

subgraph Home Assistant
    HomeAssistantCore([Home Assistant Core])
    ConfigEntryClass[/ConfigEntry/]
    AddEntitiesCallbackClass[/AddEntitiesCallback/]
    SensorEntityClass[/SensorEntity/]
    async_forward_entry_setup_ha[/async_forward_entry_setup/]
    async_track_time_interval_ha[/async_track_time_interval/]
    HomeAssistantCore -- Provides --> ConfigEntryClass
    HomeAssistantCore -- Provides --> AddEntitiesCallbackClass
    HomeAssistantCore -- Provides --> SensorEntityClass
    HomeAssistantCore -- Provides --> async_forward_entry_setup_ha
    HomeAssistantCore -- Provides --> async_track_time_interval_ha
end

subgraph aiohttp
    aiohttp_lib([aiohttp])
    ClientSessionClass[/ClientSession/]
    aiohttp_lib -- Provides --> ClientSessionClass
end

init_py -- Imports --> DOMAIN
init_py -- Calls --> async_forward_entry_setup_ha
async_setup_entry_init -- Calls --> async_forward_entry_setup_ha
async_forward_entry_setup_ha -- Forwards to --> sensor_py

sensor_py -- Imports --> DOMAIN
sensor_py -- Uses --> PLATFORM_SCHEMA
async_setup_platform_sensor -- Uses --> PLATFORM_SCHEMA
async_setup_platform_sensor -- Creates --> PVForecastCZSensor_class
async_setup_platform_sensor -- Calls --> AddEntitiesCallbackClass
PVForecastCZSensor_class -- Inherits from --> SensorEntityClass
PVForecastCZSensor_class -- Uses --> SENSOR_DESCRIPTIONS
PVForecastCZSensor_class -- Uses --> async_fetch_data_sensor
PVForecastCZSensor_class -- Uses --> ClientSessionClass
PVForecastCZSensor_class -- Calls --> async_track_time_interval_ha

async_fetch_data_sensor -- Uses --> aiohttp_lib
style HomeAssistantCore fill:#f9f,stroke:#333,stroke-width:2px
style aiohttp_lib fill:#ccf,stroke:#333,stroke-width:2px
style const_py fill:#eee,stroke:#333,stroke-width:2px
style init_py fill:#eee,stroke:#333,stroke-width:2px
style sensor_py fill:#eee,stroke:#333,stroke-width:2px
