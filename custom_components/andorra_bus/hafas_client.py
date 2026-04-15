"""HAFAS API client for Andorra Bus (feda.hafas.cloud)."""
from __future__ import annotations

import logging
import time
import random
import string
from datetime import datetime, timezone, timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    HAFAS_BASE_URL,
    HAFAS_AID,
    HAFAS_VER,
    HAFAS_CLIENT,
    MAX_DEPARTURES,
    STATION_BOARD_DURATION,
    ANDORRA_BBOX,
    ANDORRA_TZ,
)

_LOGGER = logging.getLogger(__name__)


def _random_id(length: int = 16) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class AndorraHafasClient:
    """Client for the FEDA Mou-te HAFAS API."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

    def _build_request(self, method: str, req: dict) -> dict:
        return {
            "id": _random_id(),
            "ver": HAFAS_VER,
            "lang": "cat",
            "auth": {"type": "AID", "aid": HAFAS_AID},
            "client": HAFAS_CLIENT,
            "formatted": False,
            "svcReqL": [{"meth": method, "req": req}],
        }

    async def _post(self, payload: dict) -> dict:
        session = async_get_clientsession(self._hass)
        url = f"{HAFAS_BASE_URL}?rnd={int(time.time() * 1000)}"
        try:
            async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)
                if not isinstance(data, dict):
                    _LOGGER.error("HAFAS returned non-dict: %s", type(data))
                    return {}
                if "svcResL" not in data:
                    _LOGGER.error("HAFAS missing svcResL. Keys=%s snippet=%s", list(data.keys()), str(data)[:300])
                return data
        except aiohttp.ClientError as err:
            _LOGGER.error("HAFAS request failed: %s", err)
            raise

    async def search_stops(self, query: str) -> list[dict]:
        payload = self._build_request("LocMatch", {
            "input": {"loc": {"type": "S", "name": query}, "maxLoc": 15, "field": "S"}
        })
        data = await self._post(payload)
        results = []
        try:
            loc_list = data["svcResL"][0]["res"]["match"]["locL"]
            for loc in loc_list:
                if loc.get("type") == "S":
                    results.append(_parse_stop(loc))
        except (KeyError, IndexError, TypeError) as err:
            _LOGGER.warning("Error parsing stop search: %s", err)
        return results

    async def get_all_stops(self) -> list[dict]:
        payload = self._build_request("LocGeoPos", {
            "rect": ANDORRA_BBOX, "getPOIs": False, "getStops": True, "maxLoc": 200,
        })
        data = await self._post(payload)
        results = []
        try:
            for loc in data["svcResL"][0]["res"].get("locL", []):
                if loc.get("type") == "S":
                    results.append(_parse_stop(loc))
        except (KeyError, IndexError, TypeError) as err:
            _LOGGER.warning("Error parsing all stops: %s", err)
        results.sort(key=lambda s: s["name"])
        return results

    async def search_stops_by_line(self, line_query: str) -> list[dict]:
        return await self.get_all_stops()

    async def get_departures(self, stop_id: str) -> list[dict]:
        """Get departures. Robust against missing dates in stbStop."""
        payload = self._build_request("StationBoard", {
            "type": "DEP",
            "stbLoc": {"type": "S", "state": "F", "extId": stop_id},
            "maxJny": MAX_DEPARTURES,
            "dur": STATION_BOARD_DURATION,
        })

        data = await self._post(payload)
        departures = []

        if not data or "svcResL" not in data:
            _LOGGER.warning("StationBoard stop %s: no svcResL", stop_id)
            return departures

        try:
            svc_res = data["svcResL"][0]
            err_code = svc_res.get("err", "OK")
            if err_code not in ("OK", ""):
                _LOGGER.debug("StationBoard stop %s: %s (sense servei?)", stop_id, err_code)
                return departures

            res = svc_res["res"]
            common = res.get("common", {})
            prod_list = common.get("prodL", [])
            op_list = common.get("opL", [])
            jny_list = res.get("jnyL", [])

            # The date for the board (used when individual journeys don't have date)
            board_date = res.get("date", "")

            _LOGGER.debug("StationBoard stop %s: %d journeys, board_date=%s", stop_id, len(jny_list), board_date)

            for jny in jny_list:
                try:
                    stop_info = jny.get("stbStop", {})

                    # Time strings
                    dep_time_s = stop_info.get("dTimeS", "")
                    dep_time_r = stop_info.get("dTimeR", dep_time_s)

                    # Date: prefer stbStop date, fallback to journey date, fallback to board date
                    dep_date_s = (
                        stop_info.get("dDateS")
                        or jny.get("date")
                        or board_date
                        or ""
                    )
                    dep_date_r = (
                        stop_info.get("dDateR")
                        or dep_date_s
                    )

                    planned_dt = _parse_hafas_datetime(dep_date_s, dep_time_s)
                    realtime_dt = _parse_hafas_datetime(dep_date_r, dep_time_r)

                    # If we still have no date, build a best-effort time for display
                    display_time = None
                    if planned_dt:
                        display_time = _format_local_time(planned_dt)
                    elif dep_time_s and len(dep_time_s) >= 4:
                        # Format HHMMSS → HH:MM without date
                        display_time = f"{dep_time_s[:2]}:{dep_time_s[2:4]}"

                    delay_minutes = 0
                    if planned_dt and realtime_dt:
                        delay_minutes = int((realtime_dt - planned_dt).total_seconds() / 60)

                    # Line info
                    prod_x = jny.get("prodX", 0)
                    line_info = prod_list[prod_x] if prod_x < len(prod_list) else {}
                    line_name = (
                        line_info.get("name")
                        or line_info.get("prodCtx", {}).get("num")
                        or line_info.get("number")
                        or "?"
                    )

                    op_x = line_info.get("oprX", -1)
                    operator_name = op_list[op_x].get("name", "") if 0 <= op_x < len(op_list) else ""

                    direction = jny.get("dirTxt", "")

                    now_utc = datetime.now(timezone.utc)
                    dep_dt = realtime_dt or planned_dt
                    minutes_until = int((dep_dt - now_utc).total_seconds() / 60) if dep_dt else None

                    cancelled = stop_info.get("dCncl", False) or jny.get("isCncl", False)

                    departures.append({
                        "line": line_name,
                        "direction": direction,
                        "operator": operator_name,
                        "planned_departure": planned_dt.isoformat() if planned_dt else None,
                        "realtime_departure": dep_dt.isoformat() if dep_dt else None,
                        "display_time": display_time,
                        "delay_minutes": delay_minutes,
                        "minutes_until": minutes_until,
                        "cancelled": cancelled,
                        "dep_time_raw": dep_time_s,  # kept for debug
                    })

                except Exception as err:
                    _LOGGER.debug("Error parsing journey: %s | jny=%s", err, str(jny)[:200])
                    continue

        except Exception as err:
            _LOGGER.warning("Error parsing StationBoard stop %s: %s", stop_id, err)

        departures.sort(key=lambda d: (
            d.get("realtime_departure") or d.get("dep_time_raw") or ""
        ))

        _LOGGER.debug("StationBoard stop %s: returning %d departures", stop_id, len(departures))
        return departures


def _parse_stop(loc: dict) -> dict:
    crd = loc.get("crd", {})
    return {
        "id": loc.get("extId") or loc.get("lid", ""),
        "name": loc.get("name", ""),
        "lat": crd.get("y", 0) / 1_000_000,
        "lon": crd.get("x", 0) / 1_000_000,
    }


def _format_local_time(dt_utc: datetime) -> str:
    try:
        from zoneinfo import ZoneInfo
        local_dt = dt_utc.astimezone(ZoneInfo(ANDORRA_TZ))
    except Exception:
        local_dt = dt_utc + timedelta(hours=1)
    return local_dt.strftime("%H:%M")


def _parse_hafas_datetime(date_str: str, time_str: str) -> datetime | None:
    if not date_str or not time_str:
        return None
    try:
        hour = int(time_str[:2])
        extra_days = 0
        if hour >= 24:
            extra_days = hour // 24
            time_str = f"{hour % 24:02d}{time_str[2:]}"
        dt = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
        dt += timedelta(days=extra_days)
        try:
            from zoneinfo import ZoneInfo
            dt = dt.replace(tzinfo=ZoneInfo(ANDORRA_TZ)).astimezone(timezone.utc)
        except Exception:
            dt = dt.replace(tzinfo=timezone(timedelta(hours=1))).astimezone(timezone.utc)
        return dt
    except Exception as err:
        _LOGGER.debug("Cannot parse datetime '%s' '%s': %s", date_str, time_str, err)
        return None
        