"""DataUpdateCoordinator for HoYoverse integration."""
from __future__ import annotations

import asyncio
import hashlib
import logging
import random
import string
import time
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    UPDATE_INTERVAL_MINUTES,
    GAME_GENSHIN, GAME_HSR, GAME_ZZZ, GAME_HI3,
    API_ENDPOINTS,
    DS_SALT_OVERSEAS,
    APP_VERSION,
    CONF_LTOKEN, CONF_LTUID,
    CONF_GENSHIN_UID, CONF_GENSHIN_SERVER,
    CONF_HSR_UID, CONF_HSR_SERVER,
    CONF_ZZZ_UID, CONF_ZZZ_SERVER,
    CONF_HI3_UID, CONF_HI3_SERVER,
)

_LOGGER = logging.getLogger(__name__)

GAME_UID_KEYS = {
    GAME_GENSHIN: (CONF_GENSHIN_UID, CONF_GENSHIN_SERVER),
    GAME_HSR:     (CONF_HSR_UID,     CONF_HSR_SERVER),
    GAME_ZZZ:     (CONF_ZZZ_UID,     CONF_ZZZ_SERVER),
    GAME_HI3:     (CONF_HI3_UID,     CONF_HI3_SERVER),
}


def _generate_ds(salt: str = DS_SALT_OVERSEAS) -> str:
    """Generate the DS header for HoYoLAB API authentication."""
    t = int(time.time())
    r = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()
    return f"{t},{r},{h}"


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
        self._ltoken = config[CONF_LTOKEN]
        self._ltuid = config[CONF_LTUID]

    def _get_headers(self) -> dict[str, str]:
        return {
            "Cookie": f"ltoken_v2={self._ltoken}; ltuid_v2={self._ltuid}",
            "x-rpc-app_version": APP_VERSION,
            "x-rpc-client_type": "5",
            "x-rpc-language": "en-us",
            "DS": _generate_ds(),
            "Accept": "application/json, text/plain, */*",
            "User-Agent": (
                f"Mozilla/5.0 miHoYoBBS/{APP_VERSION}"
            ),
            "Referer": "https://act.hoyolab.com",
            "Origin": "https://act.hoyolab.com",
        }

    async def _fetch_game(
        self,
        session: aiohttp.ClientSession,
        game: str,
        uid: str,
        server: str,
    ) -> dict[str, Any]:
        """Fetch real-time notes for one game."""
        url = API_ENDPOINTS[game]
        params = {"server": server, "role_id": uid}
        try:
            async with session.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                resp.raise_for_status()
                body = await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"[{game}] HTTP error: {err}") from err

        retcode = body.get("retcode", -1)
        if retcode == -100:
            raise UpdateFailed(f"[{game}] Cookie expired or invalid (retcode={retcode})")
        if retcode != 0:
            raise UpdateFailed(
                f"[{game}] API error retcode={retcode}: {body.get('message', 'unknown')}"
            )
        return body.get("data", {})

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data for all enabled games concurrently."""
        tasks: dict[str, asyncio.Task] = {}
        result: dict[str, Any] = {}

        async with aiohttp.ClientSession() as session:
            for game, (uid_key, server_key) in GAME_UID_KEYS.items():
                uid = self._config.get(uid_key, "").strip()
                server = self._config.get(server_key, "").strip()
                if uid and server:
                    tasks[game] = asyncio.create_task(
                        self._fetch_game(session, game, uid, server)
                    )

            if not tasks:
                raise UpdateFailed("No games configured")

            done = await asyncio.gather(*tasks.values(), return_exceptions=True)

        for game, outcome in zip(tasks.keys(), done):
            if isinstance(outcome, Exception):
                _LOGGER.warning("Failed to fetch %s data: %s", game, outcome)
                result[game] = None
            else:
                result[game] = outcome
                _LOGGER.debug("[%s] data fetched OK", game)

        return result
