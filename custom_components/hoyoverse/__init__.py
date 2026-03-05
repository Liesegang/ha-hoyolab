"""The HoYoverse integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import HoyoverseCoordinator

_LOGGER = logging.getLogger(__name__)

CARD_URL = f"/{DOMAIN}/hoyoverse-card.js"
CARD_FILE = Path(__file__).parent / "hoyoverse-card.js"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the static path for the card JS."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(CARD_FILE), cache_headers=True)]
    )

    # Register as a Lovelace resource
    await _register_card_resource(hass)
    return True


async def _register_card_resource(hass: HomeAssistant) -> None:
    """Add the card JS as a Lovelace resource if not already registered."""
    if "lovelace" not in hass.data:
        return

    try:
        lovelace_data = hass.data["lovelace"]
        resources = lovelace_data.resources
        if resources is None:
            return

        # Check if already registered
        existing = resources.async_items()
        for resource in existing:
            if CARD_URL in resource.get("url", ""):
                return

        await resources.async_create_item({"res_type": "module", "url": CARD_URL})
        _LOGGER.info("Registered hoyoverse-card.js as Lovelace resource")
    except Exception:  # noqa: BLE001
        _LOGGER.debug(
            "Could not auto-register Lovelace resource. "
            "Please add %s manually as a Lovelace resource.",
            CARD_URL,
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HoYoverse from a config entry."""
    coordinator = HoyoverseCoordinator(hass, dict(entry.data))
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        return True
    return False
