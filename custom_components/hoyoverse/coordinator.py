"""DataUpdateCoordinator for HoYoverse integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import genshin

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    UPDATE_INTERVAL_MINUTES,
    GAME_GENSHIN, GAME_HSR, GAME_ZZZ, GAME_HI3,
    CONF_LTOKEN, CONF_LTUID,
    CONF_GENSHIN_UID,
    CONF_HSR_UID,
    CONF_ZZZ_UID,
    CONF_HI3_UID,
)

_LOGGER = logging.getLogger(__name__)

GAME_UID_KEYS = {
    GAME_GENSHIN: CONF_GENSHIN_UID,
    GAME_HSR: CONF_HSR_UID,
    GAME_ZZZ: CONF_ZZZ_UID,
    GAME_HI3: CONF_HI3_UID,
}

GAME_FETCH = {
    GAME_GENSHIN: "get_genshin_notes",
    GAME_HSR: "get_starrail_notes",
    GAME_ZZZ: "get_zzz_notes",
    GAME_HI3: "get_honkai_notes",
}


class HoyoverseCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that fetches data from HoYoLAB for all enabled games."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )
        self._config = config
        self._client = genshin.Client(
            cookies={
                "ltoken_v2": config[CONF_LTOKEN],
                "ltuid_v2": config[CONF_LTUID],
            },
            lang="en-us",
        )

    async def _fetch_game(self, game: str, uid: int) -> Any:
        """Fetch real-time notes for one game via genshin.py."""
        method = getattr(self._client, GAME_FETCH[game])
        return await method(uid)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data for all enabled games concurrently."""
        tasks: dict[str, asyncio.Task] = {}
        result: dict[str, Any] = {}

        for game, uid_key in GAME_UID_KEYS.items():
            uid_str = self._config.get(uid_key, "").strip()
            if uid_str:
                tasks[game] = asyncio.create_task(
                    self._fetch_game(game, int(uid_str))
                )

        if not tasks:
            raise UpdateFailed("No games configured")

        done = await asyncio.gather(*tasks.values(), return_exceptions=True)

        for game, outcome in zip(tasks.keys(), done):
            if isinstance(outcome, genshin.errors.InvalidCookies):
                raise UpdateFailed(
                    f"[{game}] Cookie expired or invalid"
                ) from outcome
            if isinstance(outcome, Exception):
                _LOGGER.warning("Failed to fetch %s data: %s", game, outcome)
                result[game] = None
            else:
                result[game] = outcome
                _LOGGER.debug("[%s] data fetched OK", game)

        return result
