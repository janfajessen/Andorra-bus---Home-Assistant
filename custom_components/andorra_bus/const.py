"""Constants for the Andorra Bus integration."""

DOMAIN = "andorra_bus"

# HAFAS API endpoint discovered from feda.hafas.cloud web app
HAFAS_BASE_URL = "https://feda.hafas.cloud/bin/mgate.exe"

# Authentication token (AID) from the FEDA Mou-te web app
HAFAS_AID = "jf784LdHu4KNBfUc"

# API version
HAFAS_VER = "1.63"

# Client info as used by the web app
HAFAS_CLIENT = {
    "id": "HAFAS",
    "type": "WEB",
    "name": "webapp",
    "l": "vs_webapp",
    "v": 10005,
}

# Default update interval in seconds
DEFAULT_SCAN_INTERVAL = 90

# Number of departures to show per sensor
DEFAULT_DEPARTURES_COUNT = 5

# Maximum departures to request from API
MAX_DEPARTURES = 30

# Duration window for StationBoard in minutes (24h to catch next-day buses)
STATION_BOARD_DURATION = 1440

# Andorra timezone
ANDORRA_TZ = "Europe/Andorra"

# Andorra bounding box for LocGeoPos (HAFAS coords = degrees * 1,000,000)
ANDORRA_BBOX = {
    "llCrd": {"x": 1410000, "y": 42420000},  # SW corner
    "urCrd": {"x": 1800000, "y": 42660000},  # NE corner
}

# Search method options
SEARCH_BY_NAME = "name"
SEARCH_ALL_STOPS = "all"
SEARCH_BY_LINE = "line"
