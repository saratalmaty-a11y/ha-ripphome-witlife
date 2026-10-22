"""Light platform for RippHome / Wit Life lamps (BLE-ADV broadcast)."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.components.light import (ATTR_BRIGHTNESS, ATTR_COLOR_TEMP_KELVIN,
                                            ColorMode, LightEntity)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .codec import RippMeshCodec
from .const import (CONF_DST, CONF_HCI, CONF_KEY_ENC, CONF_KEY_PRIV, CONF_NAME,
                    CONF_REPEAT, CONF_TX, DOMAIN)

_LOGGER = logging.getLogger(__name__)

MIN_K = 2700   # warm
MAX_K = 6500   # cold


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            add_entities: AddEntitiesCallback) -> None:
    d = entry.data
    codec = RippMeshCodec(bytes.fromhex(d[CONF_KEY_ENC]),
                          bytes.fromhex(d[CONF_KEY_PRIV]),
                          bytes.fromhex(d[CONF_DST]))
    add_entities([RippHomeLight(entry, codec)])


class RippHomeLight(LightEntity):
    _attr_has_entity_name = True
    _attr_supported_color_modes = {ColorMode.COLOR_TEMP}
    _attr_color_mode = ColorMode.COLOR_TEMP
    _attr_min_color_temp_kelvin = MIN_K
    _attr_max_color_temp_kelvin = MAX_K

    def __init__(self, entry: ConfigEntry, codec: RippMeshCodec) -> None:
        self._codec = codec
        self._tx = entry.data.get(CONF_TX, "btmgmt")
        self._hci = int(entry.data.get(CONF_HCI, 0))
        self._repeat = int(entry.data.get(CONF_REPEAT, 4))
        self._attr_name = entry.data.get(CONF_NAME) or "RippHome lamp"
        self._attr_unique_id = f"{entry.entry_id}_light"
        self._is_on = False
        self._brightness = 255
        self._ct_kelvin = 4000

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def brightness(self) -> int:
        return self._brightness

    @property
    def color_temp_kelvin(self) -> int:
        return self._ct_kelvin

    async def _broadcast(self, adv: bytes) -> None:
        hexs = adv.hex()
        if self._tx == "log":
            _LOGGER.info("RippHome ADV: %s", hexs)
            return
        # btmgmt: (re)register advertising instance 1 with our AD payload
        for _ in range(max(1, self._repeat)):
            proc = await asyncio.create_subprocess_exec(
                "btmgmt", "--index", str(self._hci), "add-adv", "-d", hexs, "1",
                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE)
            _, err = await proc.communicate()
            if proc.returncode != 0:
                _LOGGER.warning("btmgmt failed (%s): %s", proc.returncode,
                                err.decode(errors="ignore").strip())
                break
            await asyncio.sleep(0.12)

    async def async_turn_on(self, **kw) -> None:
        if ATTR_BRIGHTNESS in kw:
            self._brightness = int(kw[ATTR_BRIGHTNESS])
            await self._broadcast(self._codec.brightness(self._brightness))
        if ATTR_COLOR_TEMP_KELVIN in kw:
            k = int(kw[ATTR_COLOR_TEMP_KELVIN])
            self._ct_kelvin = k
            frac = (k - MIN_K) / (MAX_K - MIN_K)
            await self._broadcast(self._codec.color_temp(round(frac * 255)))
        if ATTR_BRIGHTNESS not in kw and ATTR_COLOR_TEMP_KELVIN not in kw:
            await self._broadcast(self._codec.on())
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kw) -> None:
        await self._broadcast(self._codec.off())
        self._is_on = False
        self.async_write_ha_state()
