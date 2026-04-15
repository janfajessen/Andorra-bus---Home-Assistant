"""Sensor platform for Andorra Bus."""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_DEPARTURES_COUNT

_LOGGER = logging.getLogger(__name__)

_DAYS_CA = ["Dll", "Dm", "Dc", "Dj", "Dv", "Ds", "Dg"]


def _format_departure_time(dep: dict) -> str:
    """Format departure time smartly:
    - Same day → HH:MM
    - Tomorrow → Demà HH:MM
    - Further → Dll/Dm/... HH:MM
    """
    rt = dep.get("realtime_departure") or dep.get("planned_departure")
    if not rt:
        return "—"
    try:
        dt = datetime.fromisoformat(rt)
        try:
            from zoneinfo import ZoneInfo
            tz = ZoneInfo("Europe/Andorra")
        except Exception:
            from datetime import timezone as _tz
            tz = _tz(timedelta(hours=1))
        local_dt = dt.astimezone(tz)
        now_local = datetime.now(tz)
        time_str = local_dt.strftime("%H:%M")
        if local_dt.date() == now_local.date():
            return time_str
        elif local_dt.date() == (now_local + timedelta(days=1)).date():
            return f"Demà {time_str}"
        else:
            day_name = _DAYS_CA[local_dt.weekday()]
            return f"{day_name} {time_str}"
    except Exception:
        return dep.get("display_time", "—")


def _slugify_line(line: str) -> str:
    """Convert line name to entity-safe slug."""
    return re.sub(r"[^a-z0-9]", "_", line.lower()).strip("_")


def _get_upcoming(departures: list[dict]) -> list[dict]:
    """Return non-cancelled departures sorted by time."""
    return [
        d for d in departures
        if not d.get("cancelled")
        and (d.get("realtime_departure") or d.get("planned_departure"))
    ]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    stop_id = data["stop_id"]
    stop_name = data["stop_name"]

    main_sensor = AndorraBusMainSensor(coordinator, stop_id, stop_name, entry)
    line_sensors: dict[str, AndorraBusLineSensor] = {}

    async_add_entities([main_sensor], True)

    def _add_new_line_sensors():
        """Dynamically add a sensor for each new line found at the stop."""
        departures = coordinator.data or []
        new_entities = []
        for dep in departures:
            line = dep.get("line", "").strip()
            if not line or line == "?":
                continue
            if line not in line_sensors:
                sensor = AndorraBusLineSensor(
                    coordinator, stop_id, stop_name, line, entry
                )
                line_sensors[line] = sensor
                new_entities.append(sensor)
                _LOGGER.debug("Adding line sensor: %s at stop %s", line, stop_name)
        if new_entities:
            async_add_entities(new_entities, True)

    coordinator.async_add_listener(_add_new_line_sensors)
    if coordinator.data:
        _add_new_line_sensors()


class AndorraBusMainSensor(CoordinatorEntity, SensorEntity):
    """Main sensor showing minutes + line of next departure.
    State example: '11 min L2' / 'Ara L2' / '23:30 BN2' / 'Demà 08:00 L3'
    """

    _attr_icon = "mdi:bus-clock"

    def __init__(self, coordinator, stop_id, stop_name, entry):
        super().__init__(coordinator)
        self._stop_id = stop_id
        self._stop_name = stop_name
        self._attr_unique_id = f"{DOMAIN}_{stop_id}_next"
        self._attr_name = f"Bus {stop_name} - Propera sortida"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, stop_id)},
            "name": f"Bus: {stop_name}",
            "manufacturer": "Andorra Public Transport",
            "model": "HAFAS",
        }

    @property
    def native_value(self) -> str | None:
        upcoming = _get_upcoming(self.coordinator.data or [])
        if not upcoming:
            return None
        dep = upcoming[0]
        line = dep.get("line", "")
        minutes = dep.get("minutes_until")
        if minutes is None:
            return f"{_format_departure_time(dep)} {line}".strip()
        elif minutes <= 0:
            return f"Ara {line}".strip()
        elif minutes < 60:
            return f"{minutes} min {line}".strip()
        else:
            return f"{_format_departure_time(dep)} {line}".strip()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        upcoming = _get_upcoming(self.coordinator.data or [])
        base = {"stop_id": self._stop_id, "stop_name": self._stop_name}
        if not upcoming:
            return base
        dep = upcoming[0]
        upcoming_list = [
            {
                "line": d.get("line", ""),
                "direction": d.get("direction", ""),
                "time": _format_departure_time(d),
                "minutes_until": d.get("minutes_until"),
                "delay_minutes": d.get("delay_minutes", 0),
            }
            for d in upcoming[:DEFAULT_DEPARTURES_COUNT]
        ]
        return {
            **base,
            "line": dep.get("line"),
            "direction": dep.get("direction"),
            "minutes_until": dep.get("minutes_until"),
            "delay_minutes": dep.get("delay_minutes", 0),
            "planned_departure": dep.get("planned_departure"),
            "realtime_departure": dep.get("realtime_departure"),
            "upcoming_departures": upcoming_list,
        }


class AndorraBusLineSensor(CoordinatorEntity, SensorEntity):
    """One sensor per bus line at a stop.
    State: HH:MM (today) / 'Demà HH:MM' (tomorrow) / 'Dll HH:MM' (further).
    """

    _attr_icon = "mdi:bus"

    def __init__(self, coordinator, stop_id, stop_name, line, entry):
        super().__init__(coordinator)
        self._stop_id = stop_id
        self._stop_name = stop_name
        self._line = line
        self._attr_unique_id = f"{DOMAIN}_{stop_id}_{_slugify_line(line)}"
        self._attr_name = f"Bus {stop_name} - {line}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, stop_id)},
            "name": f"Bus: {stop_name}",
            "manufacturer": "Andorra Public Transport",
            "model": "HAFAS",
        }

    def _line_deps(self) -> list[dict]:
        all_deps = _get_upcoming(self.coordinator.data or [])
        return [d for d in all_deps if d.get("line", "").strip() == self._line]

    @property
    def native_value(self) -> str | None:
        deps = self._line_deps()
        if not deps:
            return None
        return _format_departure_time(deps[0])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        deps = self._line_deps()
        base = {
            "stop_id": self._stop_id,
            "stop_name": self._stop_name,
            "line": self._line,
        }
        if not deps:
            return base
        dep = deps[0]
        next_deps = [
            {
                "time": _format_departure_time(d),
                "minutes_until": d.get("minutes_until"),
                "direction": d.get("direction", ""),
                "delay_minutes": d.get("delay_minutes", 0),
            }
            for d in deps[:5]
        ]
        return {
            **base,
            "direction": dep.get("direction"),
            "minutes_until": dep.get("minutes_until"),
            "delay_minutes": dep.get("delay_minutes", 0),
            "planned_departure": dep.get("planned_departure"),
            "realtime_departure": dep.get("realtime_departure"),
            "next_departures": next_deps,
        }
        