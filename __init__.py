"""Andorra Bus — FEDA Mou-te integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .hafas_client import AndorraHafasClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Andorra Bus from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    stop_id = entry.data["stop_id"]
    stop_name = entry.data.get("stop_name", stop_id)
    scan_interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)

    client = AndorraHafasClient(hass)

    async def async_update_data():
        try:
            return await client.get_departures(stop_id)
        except Exception as err:
            _LOGGER.exception("Traceback fetching stop %s", stop_id)
            raise UpdateFailed(f"Error fetching departures for {stop_id}: {err}") from err
        
        
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"andorra_bus_{stop_id}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "stop_id": stop_id,
        "stop_name": stop_name,
        "client": client,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
