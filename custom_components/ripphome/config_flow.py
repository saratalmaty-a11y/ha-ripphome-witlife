"""Config flow for RippHome / Wit Life."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (CONF_DST, CONF_HCI, CONF_KEY_ENC, CONF_KEY_PRIV, CONF_NAME,
                    CONF_REPEAT, CONF_TX, DEFAULT_HCI, DEFAULT_REPEAT, DEFAULT_TX,
                    DOMAIN)


def _valid_hex(value: str, nbytes: int) -> bytes:
    b = bytes.fromhex(value.replace(" ", ""))
    if len(b) != nbytes:
        raise ValueError
    return b


class RippHomeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                _valid_hex(user_input[CONF_KEY_ENC], 16)
                _valid_hex(user_input[CONF_KEY_PRIV], 16)
                _valid_hex(user_input[CONF_DST], 2)
            except ValueError:
                errors["base"] = "invalid_hex"
            if not errors:
                await self.async_set_unique_id(
                    f"{DOMAIN}_{user_input[CONF_DST]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME) or f"RippHome {user_input[CONF_DST]}",
                    data=user_input,
                )

        schema = vol.Schema({
            vol.Required(CONF_NAME, default="RippHome lamp"): str,
            vol.Required(CONF_KEY_ENC): str,
            vol.Required(CONF_KEY_PRIV): str,
            vol.Required(CONF_DST, default="4d37"): str,
            vol.Optional(CONF_TX, default=DEFAULT_TX): vol.In(["btmgmt", "log"]),
            vol.Optional(CONF_HCI, default=DEFAULT_HCI): int,
            vol.Optional(CONF_REPEAT, default=DEFAULT_REPEAT): int,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
