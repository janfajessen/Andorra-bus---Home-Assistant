"""Config flow for Andorra Bus integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_DEPARTURES_COUNT,
    SEARCH_BY_NAME,
    SEARCH_ALL_STOPS,
    SEARCH_BY_LINE,
)
from .hafas_client import AndorraHafasClient

_LOGGER = logging.getLogger(__name__)


class AndorraBusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Andorra Bus."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self._search_results: list[dict] = []
        self._all_stops: list[dict] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: choose search method."""
        if user_input is not None:
            method = user_input.get("search_method")
            if method == SEARCH_BY_NAME:
                return await self.async_step_by_name()
            elif method == SEARCH_ALL_STOPS:
                return await self.async_step_all_stops()
            elif method == SEARCH_BY_LINE:
                return await self.async_step_by_line()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("search_method", default=SEARCH_BY_NAME): vol.In({
                    SEARCH_BY_NAME: "🔍 Cerca per nom de parada",
                    SEARCH_ALL_STOPS: "📋 Veure totes les parades d'Andorra",
                    SEARCH_BY_LINE: "🚌 Cerca per línia de bus",
                }),
            }),
        )

    async def async_step_by_name(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Search stop by name."""
        errors = {}

        if user_input is not None:
            query = user_input.get("stop_search", "").strip()
            if not query:
                errors["stop_search"] = "empty_query"
            else:
                try:
                    client = AndorraHafasClient(self.hass)
                    results = await client.search_stops(query)
                    if not results:
                        errors["stop_search"] = "no_results"
                    else:
                        self._search_results = results
                        return await self.async_step_select_stop()
                except Exception:
                    _LOGGER.exception("Error searching stops by name")
                    errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="by_name",
            data_schema=vol.Schema({
                vol.Required("stop_search"): str,
            }),
            errors=errors,
        )

    async def async_step_all_stops(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show all Andorra stops as a dropdown."""
        errors = {}

        if user_input is not None:
            selected_id = user_input.get("stop_id")
            selected = next(
                (s for s in self._all_stops if s["id"] == selected_id), None
            )
            if selected:
                return await self._create_entry(selected)

        # Fetch all stops if not already loaded
        if not self._all_stops:
            try:
                client = AndorraHafasClient(self.hass)
                self._all_stops = await client.get_all_stops()
                if not self._all_stops:
                    errors["base"] = "no_results"
            except Exception:
                _LOGGER.exception("Error fetching all stops")
                errors["base"] = "cannot_connect"

        if self._all_stops and not errors:
            stop_options = {s["id"]: s["name"] for s in self._all_stops}
            return self.async_show_form(
                step_id="all_stops",
                data_schema=vol.Schema({
                    vol.Required("stop_id"): vol.In(stop_options),
                }),
                errors=errors,
            )

        return self.async_show_form(
            step_id="all_stops",
            data_schema=vol.Schema({
                vol.Required("stop_id"): str,
            }),
            errors=errors,
        )

    async def async_step_by_line(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Search stops by line number."""
        errors = {}

        if user_input is not None:
            line_query = user_input.get("line_search", "").strip()
            if not line_query:
                errors["line_search"] = "empty_query"
            else:
                try:
                    client = AndorraHafasClient(self.hass)
                    results = await client.search_stops_by_line(line_query)
                    if not results:
                        errors["line_search"] = "no_results"
                    else:
                        self._search_results = results
                        return await self.async_step_select_stop()
                except Exception:
                    _LOGGER.exception("Error searching stops by line")
                    errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="by_line",
            data_schema=vol.Schema({
                vol.Required("line_search"): str,
            }),
            errors=errors,
        )

    async def async_step_select_stop(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select a stop from search results."""
        if user_input is not None:
            selected_id = user_input["stop_id"]
            selected = next(
                (s for s in self._search_results if s["id"] == selected_id), None
            )
            if selected:
                return await self._create_entry(selected)

        stop_options = {s["id"]: s["name"] for s in self._search_results}

        return self.async_show_form(
            step_id="select_stop",
            data_schema=vol.Schema({
                vol.Required("stop_id"): vol.In(stop_options),
            }),
            errors={},
        )

    async def _create_entry(self, stop: dict) -> FlowResult:
        """Create the config entry for a stop."""
        await self.async_set_unique_id(f"andorra_bus_{stop['id']}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=stop["name"],
            data={
                "stop_id": stop["id"],
                "stop_name": stop["name"],
                "stop_lat": stop.get("lat"),
                "stop_lon": stop.get("lon"),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow."""
        return AndorraBusOptionsFlow()


class AndorraBusOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Andorra Bus.

    NOTE: Do NOT override __init__ or store config_entry manually.
    In HA 2024.x+ self.config_entry is set automatically by the parent class.
    """

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            "scan_interval", DEFAULT_SCAN_INTERVAL
        )
        current_count = self.config_entry.options.get(
            "departures_count", DEFAULT_DEPARTURES_COUNT
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "scan_interval",
                    default=current_interval,
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=300)),
                vol.Optional(
                    "departures_count",
                    default=current_count,
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            }),
        )
